from dataclasses import dataclass, field
from typing import Dict, List, Optional
from models.card import Card, decode_cards
from datetime import datetime

@dataclass
class HandState:
    street: str
    pot: float
    board: List[Card]
    current_bet: float
    hero_cards: List[Card] = field(default_factory=list)
    last_action: Optional[dict] = None
    position: str = "BTN"  # 默认位置，实际应该从数据中获取
    
    @classmethod
    def from_dict(cls, data: dict) -> 'HandState':
        """从字典创建状态"""
        return cls(
            street=data.get("street", ""),
            pot=data.get("pot", 0),
            board=data.get("board", []),
            current_bet=data.get("current_bet", 0),
            hero_cards=data.get("hero_cards", []),
            position=data.get("position", "BTN")
        )

class GameTracker:
    def __init__(self):
        self.current_hand: Optional[HandState] = None
        self.hand_history: List[HandState] = []
        
    def process_message(self, parsed_msg: dict) -> Optional[dict]:
        try:
            msg_type = parsed_msg.get("type")
            
            if msg_type == "round_change":
                return self._handle_round_change(parsed_msg)
            elif msg_type == "action":
                return self._handle_action(parsed_msg)
                
            return {"status": "unknown_message_type"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _handle_round_change(self, data: dict) -> dict:
        if not self.current_hand or data.get("street") == "PRE_FLOP":
            self.current_hand = HandState(
                street=data.get("street", ""),
                pot=data.get("pot", 0),
                board=data.get("board", []),
                current_bet=0,
                hero_cards=data.get("hero_cards", [])
            )
        else:
            self.current_hand.street = data.get("street")
            self.current_hand.pot = data.get("pot", 0)
            if data.get("board"):
                self.current_hand.board = data.get("board")
        
        return {
            "status": "success",
            "message": "Updated hand state",
            "hand_state": self._get_state_dict()
        }
    
    def _handle_action(self, data: dict) -> dict:
        if not self.current_hand:
            return {"status": "error", "message": "No active hand"}
            
        self.current_hand.current_bet = data.get("amount", 0)
        self.current_hand.last_action = data
        
        return {
            "status": "success",
            "message": "Processed action",
            "hand_state": self._get_state_dict()
        }
        
    def _get_state_dict(self) -> dict:
        """获取状态字典"""
        if not self.current_hand:
            return {}
            
        return {
            "street": self.current_hand.street,
            "pot": self.current_hand.pot,
            "board": [str(c) for c in self.current_hand.board],
            "hero_cards": [str(c) for c in self.current_hand.hero_cards],
            "current_bet": self.current_hand.current_bet,
            "position": self.current_hand.position
        }
    
    def get_current_state(self) -> dict:
        """获取当前状态"""
        return self._get_state_dict()