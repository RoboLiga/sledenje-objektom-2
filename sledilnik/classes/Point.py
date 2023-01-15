from flask_restx import Api, fields


class Point:
    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def to_json(self):
        return {
            'x': self.x,
            'y': self.y,
        }

    def to_tuple(self) -> tuple:
        return self.x, self.y

    @classmethod
    def to_model(cls, api: Api):
        return api.model('Point', {
            'x': fields.Integer(required=True, description='x coordinate'),
            'y': fields.Integer(required=True, description='y coordinate'),
        })
