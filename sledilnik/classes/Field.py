from flask_restx import Api, fields

from sledilnik.classes.Point import Point


class Field:
    def __init__(self, top_left: Point, top_right: Point, bottom_left: Point, bottom_right: Point):
        self.top_left: Point = top_left
        self.top_right: Point = top_right
        self.bottom_left: Point = bottom_left
        self.bottom_right: Point = bottom_right

    def to_json(self):
        return {
            "top_left": self.top_left.to_json(),
            "top_right": self.top_right.to_json(),
            "bottom_left": self.bottom_left.to_json(),
            "bottom_right": self.bottom_right.to_json()
        }

    def to_tuple(self) -> tuple:
        return (
            self.top_left.to_tuple(),
            self.top_right.to_tuple(),
            self.bottom_left.to_tuple(),
            self.bottom_right.to_tuple()
        )

    @classmethod
    def to_model(cls, api: Api):
        return api.model('Field', {
            'top_left': fields.Nested(Point.to_model(api), required=True),
            'top_right': fields.Nested(Point.to_model(api), required=True),
            'bottom_left': fields.Nested(Point.to_model(api), required=True),
            'bottom_right': fields.Nested(Point.to_model(api), required=True),
        })
