from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Card:
    value: int
    suit: int
    
    SUITS = {1: '♠', 2: '♥', 3: '♣', 4: '♦'}
    VALUES = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
    
    @staticmethod
    def from_code(code: int) -> Optional['Card']:
        """从游戏编码创建卡牌"""
        if not code or code < 0:
            return None
        value = code % 100
        suit = code // 100
        return Card(value, suit)
    
    def __str__(self) -> str:
        val = self.VALUES.get(self.value, str(self.value))
        return f"{val}{self.SUITS.get(self.suit, '?')}"
        
    @classmethod
    def from_str(cls, card_str: str) -> Optional['Card']:
        """从字符串创建卡牌（用于测试）"""
        try:
            value_str = card_str[:-1]
            suit_str = card_str[-1]
            
            # 解析值
            if value_str == 'A':
                value = 1
            elif value_str == 'K':
                value = 13
            elif value_str == 'Q':
                value = 12
            elif value_str == 'J':
                value = 11
            else:
                value = int(value_str)
                
            # 解析花色
            suit_map = {'♠': 1, '♥': 2, '♣': 3, '♦': 4}
            suit = suit_map.get(suit_str, 0)
            
            return cls(value, suit)
        except:
            return None

def decode_cards(card_codes: List[int]) -> List[Card]:
    """解码多张卡牌"""
    cards = []
    for code in card_codes:
        if code > 0:
            card = Card.from_code(code)
            if card:
                cards.append(card)
    return cards