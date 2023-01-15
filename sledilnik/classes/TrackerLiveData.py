from typing import Dict

from sledilnik.classes import ObjectTracker


class TrackerLiveData:
    def __init__(self, fields: Dict):
        self.fields = fields
        self.objects: Dict[int, ObjectTracker] = {}

    def to_json(self):
        return {
            "fields": {str(field_id): field for field_id, field in self.fields.items()},
            "objects": {str(object_id): game_object.to_json() for object_id, game_object in self.objects.items()}
        }
