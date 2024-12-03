import pytest
from core.parser import HandHistoryParser

def test_parse_round_change():
    parser = HandHistoryParser()
    sample_message = '''{"msgType": "WP_roundChangeNotify", "msgBody": {
        "round": "PRE_FLOP", "totalPot": 3, "dealPublicCards": [101, 213, 308]
    }}'''
    
    result = parser.parse_message(sample_message)
    
    assert result is not None
    assert result["type"] == "round_change"
    assert result["pot"] == 3
    assert len(result["board"]) == 3
