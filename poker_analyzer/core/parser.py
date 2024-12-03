import json
from typing import Optional
from models.card import Card, decode_cards

class HandHistoryParser:
    def parse_message(self, msg: str) -> Optional[dict]:
        try:
            if not msg or "msgType" not in msg:
                return None
                
            data = json.loads(msg)
            msg_type = data.get("msgType")
            
            parsers = {
                "WP_roundChangeNotify": self._parse_round_change,
                "WP_actionNotify": self._parse_action,
                "WP_updateUserProfileNotify": self._parse_player_stats
            }
            
            parser = parsers.get(msg_type)
            return parser(data) if parser else None
            
        except Exception as e:
            print(f"Error parsing message: {e}")
            return None
    
    def _parse_round_change(self, data: dict) -> dict:
        msg_body = data.get("msgBody", {})
        hero_cards = []
        
        # 提取玩家手牌
        for player in msg_body.get("userCardsList", []):
            if player.get("handCards"):
                hero_cards = decode_cards(player.get("handCards", []))
                break
        
        return {
            "type": "round_change",
            "street": msg_body.get("round"),
            "pot": msg_body.get("totalPot", 0),
            "board": decode_cards(msg_body.get("dealPublicCards", [])),
            "hero_cards": hero_cards
        }
    
    def _parse_action(self, data: dict) -> dict:
        msg_body = data.get("msgBody", {})
        action = msg_body.get("actionList", [{}])[0]
        return {
            "type": "action",
            "action_type": action.get("actionType"),
            "amount": action.get("actionScore", 0),
            "user_id": action.get("userId"),
            "position": action.get("seatNum")
        }
    
    def _parse_player_stats(self, data: dict) -> dict:
        stats = []
        msg_body = data.get("msgBody", {})
        for player in msg_body.get("listData", []):
            stats.append({
                "user_id": player.get("userId"),
                "total_hands": player.get("totalHand", 0),
                "pooling_hands": player.get("poolingHandNum", 0),
                "win_num": player.get("winNum", 0),
                "showdown_num": player.get("showdownNum", 0)
            })
        return {"type": "player_stats", "stats": stats}
