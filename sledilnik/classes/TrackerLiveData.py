from typing import Dict

from sledilnik.classes import ObjectTracker
from sledilnik.classes.Field import Field


class TrackerLiveData:
    def __init__(self, fields: Dict[int, Field]):
        self.fields: Dict[int, Field] = fields
        self.objects: Dict[int, ObjectTracker] = {}
        self.delay = None

    def to_json(self):
        return {
            "fields": {str(field_id): field.to_json() for field_id, field in self.fields.items()},
            "objects": {str(object_id): game_object.to_json() for object_id, game_object in self.objects.items()},
            "delay": self.delay
        }
