import getopt
import json
import os
import pickle
import sys
from timeit import default_timer as timer
from typing import List

import numpy as np

from sledilnik.Resources import ResKeys
from sledilnik.Tracker import Tracker
from sledilnik.classes.Field import Field
from sledilnik.classes.Point import Point
from sledilnik.classes.VideoStreamer import VideoStreamer
from sledilnik.draw_utils import *


class TrackerSetup(Tracker):
    def __init__(self, tracker_config='./tracker_config.yaml', game_config=None):
        super().__init__(tracker_config, game_config)
        self.debug = self.tracker_config['debug']

        if self.game_config is not None:
            self.fields_names = self.game_config['fields_names']
        else:
            self.fields_names = ['game_field', 'team_1_basket', 'team_2_basket']

        self.fields_corners = []
        self.fields = {}
        if os.path.isfile(self.tracker_config['fields_path']):
            print(f'Loading fields from {self.tracker_config["fields_path"]}')
            saved_fields = pickle.load(open(self.tracker_config['fields_path'], 'rb'))
            self.fields_corners = saved_fields['fields_corners']
            self.fields = saved_fields['fields']

        self.field_guide_index = 0
        self.field_guides = []
        for field in self.fields_names:
            self.field_guides.extend(create_guide_text(field))
        self.field_guides.append(self.field_guides[0])

        self.should_quit = False
        self.edit_mode = False
        self.frame_counter = 0

    def start(self):
        # Load video
        cap = VideoStreamer()
        cap.start(self.tracker_config['video_source'])

        # Create window
        cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)

        ts = timer()
        while not self.should_quit and cap.running:

            # Load frame-by-frame
            frame, timestamp = cap.read()
            if frame is None:
                if self.debug:
                    cap.stop()
                    cap = VideoStreamer()
                    cap.start(self.tracker_config['video_source'])
                    continue
                break

            # Convert to grayscale for Aruco detection
            self.frame_counter += 1
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if self.tracker_config['undistort']:
                frame = self.undistort(frame)

            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)

            # If we set all the corners, dump the latest map into file
            if self.edit_mode and len(self.fields_corners) == len(self.fields_names) * 4:
                self.save_fields()
                self.edit_mode = not self.edit_mode
                cv2.setMouseCallback(ResGUIText.sWindowName, lambda *args: None)

            # Draw GUI and objects
            self.draw_overlay(frame)

            # Process keys
            self.on_key_press()

            # Computer and display FPS
            te = timer()
            fps = 1 / (te - ts)
            draw_fps(frame, fps)
            ts = te

            # Update timestamp
            #self.data.timestamp = timestamp

            # Show frame
            cv2.imshow(ResGUIText.sWindowName, frame)

        cap.stop()
        cv2.destroyAllWindows()
        sys.exit(0)

    def draw_overlay(self, frame):
        draw_lines(frame, self.fields_corners)
        draw_help(frame)

        if self.edit_mode:
            draw_guide(frame, self.field_guides[self.field_guide_index])

    def on_click(self, event, x, y, flags, param):
        if self.edit_mode and event == cv2.EVENT_LBUTTONDOWN:
            self.fields_corners.append([x, y])
            self.field_guide_index += 1

    def on_key_press(self):
        # Detect key press
        key_pressed = cv2.waitKey(1) & 0xFF

        # Edit Map mode
        if key_pressed == ord(ResKeys.editMapKey):
            self.edit_mode = not self.edit_mode
            if self.edit_mode:
                self.fields_corners.clear()
                self.field_guide_index = 0
                cv2.setMouseCallback(ResGUIText.sWindowName, self.on_click)

        # Quit
        elif key_pressed == ord(ResKeys.quitKey):
            self.should_quit = True

    def save_fields(self):
        """
        This method creates fields from the corners of the fields and saves them to a file.
        """

        transformation_matrix = cv2.getPerspectiveTransform(
            np.array(self.fields_corners[0:4], np.float32),
            np.array(self.tracker_config['map_virtual_corners'], np.float32),
        )

        self.fields = {}
        for i, field_name in enumerate(self.fields_names):
            field = []
            for j in range(4):
                field.append(Point(*self.move_origin(*self.fields_corners[i * 4 + j], transformation_matrix)))

            self.fields[field_name] = Field(*field)

        with open(self.tracker_config['fields_path'], 'wb') as output:
            pickle.dump(
                {
                    'transformation_matrix': transformation_matrix,
                    'fields_corners': self.fields_corners,
                    'fields': self.fields
                },
                output,
                pickle.HIGHEST_PROTOCOL
            )

        print(self.fields)
