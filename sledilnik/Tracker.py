import cv2
import numpy as np
import yaml


class Tracker:
    def __init__(self, tracker_config, game_config):
        self.tracker_config = self.read_config(tracker_config)
        if game_config is not None:
            self.game_config = self.read_config(game_config)
        else:
            self.game_config = None

    @staticmethod
    def read_config(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def undistort(self, img):

        c = self.tracker_config['camera']
        # Camera parameters
        k1 = c['k1']
        k2 = c['k2']
        k3 = c['k3']
        p1 = c['p1']
        p2 = c['p2']
        fx = c['fx']
        fy = c['fy']
        cx = c['cx']
        cy = c['cy']

        dist = np.array([k1, k2, p1, p2, k3])
        mtx = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

        # Setting the params
        h, w = img.shape[:2]
        new_camera_tx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))

        # Undistort
        map_x, map_y = cv2.initUndistortRectifyMap(mtx, dist, None, new_camera_tx, (w, h), 5)
        dst = cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)

        # Crop the image
        x, y, w, h = roi
        dst = dst[y:y + h, x:x + w]
        return dst

    def move_origin(self, x, y, transformation_matrix: np.ndarray):
        """Translates coordinate to new coordinate system and applies scaling to get units in ~mm.
        Args:
            x (int): x coordinate
            y (int): y coordinate
            transformation_matrix: game field object
        Returns:
            Tuple[int, int]: Corrected coordinates
        """
        # Translate coordinates if new origin exists (top left corner of map)
        # if len(map.fieldCorners) == 12:

        s_point = np.array([np.array([[x, y]], np.float32)])
        d_point = cv2.perspectiveTransform(s_point, transformation_matrix)
        x = d_point[0][0][0]
        y = d_point[0][0][1]
        return int(round(x)), int(round(y))

    # def reverseCorrect(self, x, y, map):
    #     """Reverses the correction of the coordinates.
    #     Scale0 and scale1 define scaling constants. The scaling factor is a linear function of distance from center.
    #     Args:
    #         x (int): x coordinate
    #         y (int): y coordinate
    #         map (ResMap) : map object
    #     Returns:
    #         Tuple[int, int]: Reverted coordinates
    #     """
    #
    #     # Scaling factors
    #     scale0 = self.cameraConfig.scale0
    #     scale1 = self.cameraConfig.scale1
    #
    #     # Convert screen coordinates to 0-based coordinates
    #     offset_x = map.imageWidth / 2
    #     offset_y = map.imageHeighth / 2
    #
    #     # Calculate distance from center
    #     dist = np.sqrt((x - offset_x) ** 2 + (y - offset_y) ** 2)
    #
    #     # Find the distance before correction
    #     distOld = (-scale0 + np.sqrt(scale0 ** 2 + 4 * dist * scale1)) / (2 * scale1)
    #
    #     # Revert coordinates and return
    #     return (int(round((x - offset_x) / (scale0 + scale1 * distOld) + offset_x)),
    #             int(round((y - offset_y) / (scale0 + scale1 * distOld) + offset_y)))
