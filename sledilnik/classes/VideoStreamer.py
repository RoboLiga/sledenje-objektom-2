import threading
import time
import cv2


class VideoStreamer:
    """Fetches video from camera"""

    def __init__(self):
        self.ret = None
        self.frame = None
        self.timestamp = None
        self.video = None
        self.running = False
        return

    def __del__(self):
        if self.video.isOpened():
            self.video.release()
        return

    def start(self, src):
        # Initialize the video camera stream and read the first frame
        self.video = cv2.VideoCapture(src)
        if not self.video.isOpened():
            # Camera failed
            raise IOError("Couldn't open video file or webcam.")
        self.ret, self.frame = self.video.read()
        self.timestamp = time.time()
        if not self.ret:
            self.video.release()
            raise IOError("Couldn't open video frame.")
        self.running = True

        # Start the thread to read frames from the video stream
        t = threading.Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        try:
            # Keep looping infinitely until the stream is closed
            while self.running:
                #  Read the next frame from the stream
                self.ret, self.frame = self.video.read()
                self.timestamp = time.time()
        except:
            import traceback
            traceback.print_exc()
            self.running = False
        finally:
            # If the thread indicator variable is set, stop the thread
            self.video.release()
        return

    def read(self):
        # Return the frame most recently read
        return self.frame, self.timestamp

    def stop(self):
        self.running = False
        if self.video.isOpened():
            self.video.release()
        return
