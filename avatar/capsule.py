import json


class Capsule:
    def __init__(self):
        pass

    @staticmethod
    def tojson(status, obj):
        exp = {"status": status, "content": obj}
        return json.dumps(exp)
