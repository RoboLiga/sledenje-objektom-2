"""Provides ObjectTracker class which implements Kalman filter"""
from math import atan2, pi
from typing import Dict

import numpy as np
from flask_restx import Api, fields
from numpy.linalg import inv

from sledilnik.classes.Point import Point


class ObjectTracker:
    """Tracks object using Kalman filter"""

    def __init__(self, object_id, position, velocity, config: Dict, accel=(0, 0, 0, 0)):
        self.id = object_id
        self.position: Point = Point(position[0], position[1])
        self.bounding_box: tuple[int] = position
        self.velocity = velocity
        self.direction = atan2(position[3] - position[1], position[2] - position[0])

        self.q = np.array([[position[0]], [position[1]], [velocity[0]], [velocity[1]], [accel[0]], [accel[1]]])
        self.q2 = np.array([[position[2]], [position[3]], [velocity[2]], [velocity[3]], [accel[2]], [accel[3]]])

        self.acc_noise_magnitude = config['acc_noise_mag']
        self.dt = config['dt']
        self.u = config['u']
        self.detected = True
        self.enabled = True
        self.last_seen = 0
        self.lost_frames = 0

        self.ez = np.array(
            [
                [config['measurement_noise_x'], 0],
                [0, config['measurement_noise_y']]
            ]
        )

        self.ex = np.array(
            [
                [self.dt ** 5 / 20, 0, self.dt ** 4 / 8, 0, self.dt ** 3 / 6, 0],
                [0, self.dt ** 5 / 20, 0, self.dt ** 4 / 8, 0, self.dt ** 3 / 6],
                [self.dt ** 4 / 8, 0, self.dt ** 3 / 3, 0, self.dt ** 2 / 2, 0],
                [0, self.dt ** 4 / 8, 0, self.dt ** 3 / 3, 0, self.dt ** 2 / 2],
                [self.dt ** 3 / 6, 0, self.dt ** 2 / 2, 0, self.dt, 0],
                [0, self.dt ** 3 / 6, 0, self.dt ** 2 / 2, 0, self.dt]
            ]
        ) * self.acc_noise_magnitude ** 2 / 3

        self.p = self.ex
        self.pw = self.ex

        self.a = np.array(
            [
                [1, 0, self.dt, 0, self.dt ** 2 / 2, 0],
                [0, 1, 0, self.dt, 0, self.dt ** 2 / 2],
                [0, 0, 1, 0, self.dt, 0],
                [0, 0, 0, 1, 0, self.dt],
                [0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 1]
            ]
        )
        self.b = np.array(
            [
                [self.dt ** 2 / 2],
                [self.dt ** 2 / 2],
                [self.dt],
                [self.dt]
            ]
        )
        self.c = np.array(
            [
                [1, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 0]
            ]
        )

    def update_state(self, position):
        self.q = np.dot(self.a, self.q)  # +self.B*self.u
        self.q2 = np.dot(self.a, self.q2)  # +self.B*self.u

        self.pw = np.dot(np.dot(self.a, self.pw), np.transpose(self.a)) + self.ex
        self.p = np.dot(np.dot(self.a, self.p), np.transpose(self.a)) + self.ex

        k = np.dot(np.dot(self.p, np.transpose(self.c)),
                   inv(np.dot(np.dot(self.c, self.p), np.transpose(self.c)) + self.ez))
        k2 = np.dot(np.dot(self.pw, np.transpose(self.c)),
                    inv(np.dot(np.dot(self.c, self.pw), np.transpose(self.c)) + self.ez))
        if position:
            q_pos_measurement = np.array([[position[0]], [position[1]]])
            q_pos_measurement2 = np.array([[position[2]], [position[3]]])
            self.q = self.q + np.dot(k, q_pos_measurement - np.dot(self.c, self.q))
            self.q2 = self.q2 + np.dot(k2, q_pos_measurement2 - np.dot(self.c, self.q2))

        self.p = np.dot(np.eye(6) - np.dot(k, self.c), self.p)
        self.pw = np.dot(np.eye(6) - np.dot(k2, self.c), self.pw)
        self.velocity = (self.q[2][0], self.q[3][0])

        if not position:
            self.bounding_box = (self.q[0][0], self.q[1][0], self.q2[0][0], self.q2[1][0])
        else:
            self.bounding_box = position

        self.position = Point(self.bounding_box[0], self.bounding_box[1])
        self.direction = atan2(self.bounding_box[3] - self.bounding_box[1], self.bounding_box[2] - self.bounding_box[0])

    def to_json(self):
        return {
            "id": int(self.id),
            "position": Point(self.bounding_box[0], self.bounding_box[1]).to_json(),
            "dir": float(self.direction * 180 / pi)
        }

    @classmethod
    def to_model(cls, api: Api):
        return api.model('ObjectTracker', {
            'id': fields.Integer,
            'position': fields.Nested(Point.to_model(api)),
            'dir': fields.Float
        })
