#!/usr/bin/env python
import copy
import os
import pickle
import sys

import cv2
import cv2.aruco as aruco
import numpy as np

from sledilnik.Resources import ResGUIText, ResKeys
from sledilnik.Tracker import Tracker
from sledilnik.classes.ObjectTracker import ObjectTracker
from sledilnik.classes.TrackerLiveData import TrackerLiveData
from sledilnik.classes.VideoStreamer import VideoStreamer


class TrackerGame(Tracker):
    def __init__(self, tracker_config='./tracker_config.yaml', game_config=None):
        super().__init__(tracker_config, game_config)
        self.debug = self.tracker_config['debug']

        if os.path.isfile(self.tracker_config['fields_path']):
            print(f'Loading fields from {self.tracker_config["fields_path"]}')
            saved_fields = pickle.load(open(self.tracker_config['fields_path'], "rb"))
            self.transformation_matrix = saved_fields['transformation_matrix']
            self.data = TrackerLiveData(saved_fields['fields'])
        else:
            raise FileNotFoundError(f"Fields file ({self.tracker_config['fields_path']}) not found.")

        self.should_quit = False
        self.edit_mode = False
        self.frame_counter = 0

    def start(self, queue=None):
        # Load video
        cap = VideoStreamer()
        cap.start(self.tracker_config['video_source'])

        # Create window
        if self.debug:
            cv2.namedWindow(ResGUIText.sWindowName, cv2.WINDOW_NORMAL)
        # cv2.resizeWindow(ResGUIText.sWindowName, 2000,1000)

        while not self.should_quit and cap.running:

            # Load frame-by-frame
            frame = cap.read()
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

            # Undistort image
            if self.tracker_config['undistort']:
                frame = self.undistort(frame)

            # Detect markers
            corners_tracked, ids, rejected_img_points = aruco.detectMarkers(
                frame,
                cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100),
                parameters=self.init_aruco_parameters()
            )

            # Compute mass centers and orientation
            points_tracked = self.get_mass_center(corners_tracked, ids, frame)

            # Detect Validate and track game_objects on map
            self.track(points_tracked)

            # Write game data
            if queue is not None:
                queue.put(copy.deepcopy(self.data))
            # print(self.data.to_json())

            self.on_key_press()

            if self.debug:
                # Draw GUI and game_objects
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                frame_markers = aruco.drawDetectedMarkers(frame.copy(), corners_tracked, ids)
                # Show frame
                cv2.imshow(ResGUIText.sWindowName, frame_markers)

        # When everything done, release the capture
        cap.stop()
        cv2.destroyAllWindows()
        if queue is not None:
            queue.cancel_join_thread()
        sys.exit(0)

    def track(self, points_tracked):
        for ct in points_tracked:
            object_id = ct[0]
            position = ct[1]
            if object_id in self.data.objects:
                self.data.objects[object_id].update_state(position)
                self.data.objects[object_id].detected = True
                self.data.objects[object_id].enabled = True
                self.data.objects[object_id].last_seen = self.frame_counter
            else:
                self.data.objects[object_id] = ObjectTracker(
                    object_id,
                    position,
                    (0, 0, 0, 0),
                    self.tracker_config['kalman_filter']
                )

        # Disable object tracking if not detected for a long time
        for k, v in list(self.data.objects.items()):
            if ((self.frame_counter - v.last_seen) > self.tracker_config['object_timeout']) or \
                    not self.is_valid_pos(v.bounding_box[0:2]):
                del self.data.objects[k]
                # objects[k].enabled = False

        # Track undetected objects
        for obj in self.data.objects:
            if not self.data.objects[obj].detected:
                self.data.objects[obj].lost_frames = self.data.objects[obj].lost_frames + 1
                # if objects[obj].enabled == True:
                self.data.objects[obj].update_state([])
            self.data.objects[obj].detected = False

    def init_aruco_parameters(self):
        c = self.tracker_config['aruco_detector']
        aruco_parameters = aruco.DetectorParameters()
        aruco_parameters.adaptiveThreshWinSizeMin = c['adaptive_thresh_win_size_min']
        aruco_parameters.adaptiveThreshWinSizeMax = c['adaptive_thresh_win_size_max']
        aruco_parameters.adaptiveThreshConstant = c['adaptive_thresh_constant']
        aruco_parameters.minMarkerPerimeterRate = c['min_marker_perimeter_rate']
        aruco_parameters.maxMarkerPerimeterRate = c['max_marker_perimeter_rate']
        aruco_parameters.perspectiveRemovePixelPerCell = c['perspective_remove_pixel_per_cell']
        aruco_parameters.perspectiveRemoveIgnoredMarginPerCell = c['perspective_remove_ignored_margin_per_cell']
        aruco_parameters.minMarkerDistanceRate = c['min_marker_distance_rate']
        return aruco_parameters

    def correct(self, x, y, frame):
        """Corrects the coordinates.
        Scale0 and scale1 define scaling constants. The scaling factor is a linear function of distance from center.
        Args:
            x (int): x coordinate
            y (int): y coordinate
            frame: frame object
        Returns:
            Tuple[int, int]: Corrected coordinates
        """

        # Scaling factors
        scale0 = self.tracker_config['camera']['scale0']
        scale1 = self.tracker_config['camera']['scale1']

        # Convert screen coordinates to 0-based coordinates
        offset_x = frame.shape[1] / 2
        offset_y = frame.shape[0] / 2

        # Calculate distance from center
        dist = np.sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)

        # Correct coordinates and return
        return (int(round((x - offset_x) * (scale0 + scale1 * dist) + offset_x)),
                int(round((y - offset_y) * (scale0 + scale1 * dist) + offset_y)))

    def get_mass_center(self, corners, ids, frame):
        """Computes mass centers of objects in the frame.
        Args:
            corners (2d array of float): corners of each object in the frame
            ids (2d array of int): aruco tag ids
            frame: frame object
        Returns:
            List[int, Tuple[float, float, float, float]]: List of aruco tag ids with object center and top coordinates
        """
        mass_centers = []
        for i, o in enumerate(corners):
            x1 = o[0][0][0]
            y1 = o[0][0][1]
            x2 = o[0][1][0]
            y2 = o[0][1][1]
            x3 = o[0][2][0]
            y3 = o[0][2][1]
            x4 = o[0][3][0]
            y4 = o[0][3][1]

            # A=1/2*(x1*y2-x2*y1+x2*y3-x3*y2+x3*y4-x4*y3+x4*y1-x1*y4);
            # Cx=1/(6*A)*((x1+x2)*(x1*y2-x2*y1)+ \
            # (x2+x3)*(x2*y3-x3*y2)+ \
            # (x3+x4)*(x3*y4-x4*y3)+ \
            # (x4+x1)*(x4*y1-x1*y4))
            (Cx, Cy) = self.move_origin(
                *self.correct((x1 + x2 + x3 + x4) / 4, (y1 + y2 + y3 + y4) / 4, frame),
                self.transformation_matrix

            )
            (CxTop, CyTop) = self.move_origin(
                *self.correct((x1 + x2) / 2, (y1 + y2) / 2, frame),
                self.transformation_matrix
            )
            mass_centers.append([ids[i][0], (Cx, Cy, CxTop, CyTop)])

        return mass_centers

    def is_valid_pos(self, pos):
        return self.tracker_config['pos_limit_x'][0] <= pos[0] <= self.tracker_config['pos_limit_x'][1] and \
            self.tracker_config['pos_limit_y'][0] <= pos[1] <= self.tracker_config['pos_limit_y'][1]

    def on_key_press(self):
        # Detect key press
        key_pressed = cv2.waitKey(1) & 0xFF
        self.should_quit = key_pressed == ord(ResKeys.quitKey)