from dataclasses import dataclass
from typing import List
from .card import Card

@dataclass
class PlayerState:
    user_id: int
    nickname: str
    position: str
    stack: float
    cards: List[Card]
    vpip: float = 0.0
    pfr: float = 0.0
    wwsf: float = 0.0  # 看牌率
    af: float = 0.0    # 攻击因子
    hands_played: int = 0
    
    def update_stats(self, stats_data: dict):
        """更新玩家统计数据"""
        total_hands = stats_data.get("totalHand", 1)
        self.hands_played = total_hands
        self.vpip = round(stats_data.get("poolingHandNum", 0) / max(total_hands, 1) * 100, 2)
        self.wwsf = round(stats_data.get("showdownNum", 0) / max(total_hands, 1) * 100, 2)