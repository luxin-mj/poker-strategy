# utils/helpers.py
from json import JSONEncoder
from models.card import Card

class PokerJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Card):
            return str(obj)
        return super().default(obj)