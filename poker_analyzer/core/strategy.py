from typing import List, Dict, Optional
from models.card import Card

class StrategyEngine:
    def __init__(self):
        self.position_weights = {
            'BTN': 1.2,  # 按钮位置最有利
            'CO': 1.1,   # 枪口位置次之
            'MP': 0.9,   # 中间位置较差
            'UTG': 0.8,  # 首位位置最差
            'BB': 0.7,   # 大盲位置被动
            'SB': 0.6    # 小盲位置最差
        }
        
        self.postflop_thresholds = {
            'bet_for_value': 0.7,    # 价值下注阈值
            'bet_as_bluff': 0.3,     # 诈唬下注阈值
            'call_bet': 0.5,         # 跟注阈值
            'raise_bet': 0.8         # 加注阈值
        }
        
        self.board_textures = {
            'coordinated': 0.8,      # 同花或者连牌的公共牌
            'dynamic': 0.7,          # 高牌或者差值小的公共牌
            'static': 0.6           # 不连续且无同花的公共牌
        }
    
    def get_advice(self, game_state: dict) -> dict:
        try:
            street = game_state.get("street")
            hero_cards = game_state.get("hero_cards", [])
            board = game_state.get("board", [])
            pot = game_state.get("pot", 0)
            position = game_state.get("position", "BTN")
            
            # 解析手牌
            cards = [Card.from_str(card) for card in hero_cards]
            cards = [card for card in cards if card is not None]
            
            if not cards:
                return {"error": "Invalid hero cards"}
                
            if street != "PRE_FLOP":
                # 解析公共牌
                board_cards = [Card.from_str(card) for card in board]
                board_cards = [card for card in board_cards if card is not None]
                
                # 分析和生成建议
                analysis = self._analyze_hand(cards, board_cards)
                advice = self._generate_advice(analysis, cards, board_cards, position, pot, street)
                
                return advice
            else:
                return self._preflop_analyze(cards, position, pot)
                
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            return {"error": f"Error in get_advice: {str(e)}"}
    
    def _analyze_hand(self, cards: List[Card], board: List[Card]) -> dict:
        """分析手牌和公共牌"""
        
        # 计算出口数
        straight_outs = self._count_straight_outs(cards + board)
        flush_outs = self._count_flush_outs(cards + board)
        
        # 计算总体权益
        equity = 0.0
        
        # 顺子听牌权益
        if straight_outs > 0:
            if len(board) == 3:  # 翻牌圈
                equity += (straight_outs / 47.0) * 0.9
            else:
                equity += (straight_outs / 47.0) * 0.8
        
        # 同花听牌权益
        if flush_outs > 0:
            if len(board) == 3:
                equity += (flush_outs / 47.0) * 0.95
            else:
                equity += (flush_outs / 47.0) * 0.85
        
        return {
            'straight_outs': straight_outs,
            'flush_outs': flush_outs,
            'equity': min(equity, 1.0)
        }
    
    def _generate_advice(self, analysis: dict, cards: List[Card], board: List[Card],
                        position: str, pot: float, street: str) -> dict:
        """生成策略建议"""
        equity = analysis['equity'] * self.position_weights.get(position, 1.0)
        board_texture = self._analyze_board_texture(board)
        
        details = []
        
        # 基本强度分析
        if equity > 0.7:
            strength_desc = "强牌"
        elif equity > 0.5:
            strength_desc = "中等强度"
        else:
            strength_desc = "弱牌"
            
        details.append(f"手牌强度: {strength_desc} ({equity:.2f})")
        
        # 听牌分析
        if analysis['straight_outs'] > 0:
            outs_percentage = (analysis['straight_outs'] / 47.0) * 100
            details.append(f"顺子听牌: {analysis['straight_outs']}张出口 ({outs_percentage:.1f}%命中率)")
        
        if analysis['flush_outs'] > 0:
            outs_percentage = (analysis['flush_outs'] / 47.0) * 100
            details.append(f"同花听牌: {analysis['flush_outs']}张出口 ({outs_percentage:.1f}%命中率)")
            
        # 牌面分析
        details.append(f"牌面特征: {board_texture['description']}")
        
        # 位置分析
        if position in ['BTN', 'CO']:
            details.append("位置优势: 后手位置有利于控制底池")
            
        # 确定行动建议
        if equity > self.postflop_thresholds['bet_for_value']:
            action = "BET"
            size = pot * 0.75
            reason = "价值下注"
            if board_texture['coordinated']:
                size = pot * 0.8
                reason += " (协调牌面加大下注尺度)"
        else:
            action = "CHECK"
            size = 0
            reason = "保护听牌权益" if analysis['straight_outs'] > 0 else "对手范围领先"
            
        return {
            "action": action,
            "size": size,
            "reason": f"{street}圈{action} - {reason}\n分析:\n" + "\n".join(f"- {d}" for d in details),
            "hand_strength": equity,
            "analysis": analysis
        }
    
    def _analyze_board_texture(self, board: List[Card]) -> dict:
        """分析牌面特征"""
        if len(board) < 3:
            return {"coordinated": False, "description": "等待更多公共牌"}
            
        values = sorted([c.value for c in board])
        suits = [c.suit for c in board]
        
        # 检查同花可能
        suited = len(set(suits)) <= 2
        
        # 检查连牌可能
        connected = max(values) - min(values) <= 4
        
        # 检查高牌比例
        high_cards = len([v for v in values if v in [1, 10, 11, 12, 13]])
        
        description = []
        if suited:
            description.append("同花可能")
        if connected:
            description.append("顺子可能")
        if high_cards >= 2:
            description.append("高牌密集")
            
        if not description:
            description = ["分散的牌面"]
            
        return {
            "coordinated": suited or connected,
            "high_card_heavy": high_cards >= 2,
            "description": " | ".join(description)
        }
    
    def _count_straight_outs(self, cards: List[Card]) -> int:
        """计算顺子听牌数"""
        values = sorted(list(set([c.value for c in cards])))
        if 1 in values:
            values.append(14)
            
        outs = 0
        for i in range(len(values) - 3):
            window = values[i:i+4]
            if max(window) - min(window) <= 4:
                # 找缺口
                for v in range(min(window)-1, max(window)+2):
                    if v > 0 and v <= 14 and v not in window:
                        outs += 1
                        
        return outs
    
    def _count_flush_outs(self, cards: List[Card]) -> int:
        """计算同花听牌数"""
        suits = [c.suit for c in cards]
        for suit in set(suits):
            if suits.count(suit) == 4:
                return 9
        return 0
    
    def _preflop_analyze(self, cards: List[Card], position: str, pot: float) -> dict:
        """翻前分析"""
        strength = self._calculate_hand_strength(cards)
        position_factor = self.position_weights.get(position, 1.0)
        adjusted_strength = strength * position_factor
        
        if adjusted_strength > 0.7:
            return {
                "action": "RAISE",
                "size": max(3, pot * 0.75),
                "reason": f"强力起手牌 {str(cards[0])}{str(cards[1])} (强度: {strength:.2f}, 位置: {position})",
                "hand_strength": adjusted_strength
            }
        elif adjusted_strength > 0.5:
            return {
                "action": "CALL",
                "size": 0,
                "reason": f"可玩起手牌 {str(cards[0])}{str(cards[1])} (强度: {strength:.2f}, 位置: {position})",
                "hand_strength": adjusted_strength
            }
        else:
            return {
                "action": "FOLD",
                "size": 0,
                "reason": f"弱起手牌 {str(cards[0])}{str(cards[1])} (强度: {strength:.2f}, 位置: {position})",
                "hand_strength": adjusted_strength
            }
            
    def _calculate_hand_strength(self, cards: List[Card]) -> float:
        """计算手牌强度"""
        if len(cards) != 2:
            return 0.0
            
        values = sorted([c.value for c in cards], reverse=True)
        suited = cards[0].suit == cards[1].suit
        
        if values[0] == values[1]:
            if values[0] == 1:
                return 1.0
            return 0.5 + (values[0] / 28.0)
            
        if 1 in values:
            values = [14 if v == 1 else v for v in values]
            
        base = (max(values) / 28.0) + (min(values) / 56.0)
        
        if suited:
            base *= 1.1
            
        gap = abs(values[0] - values[1])
        if gap == 1:
            base *= 1.2
        elif gap == 2:
            base *= 1.1
        elif gap > 4:
            base *= 0.8
            
        return min(base, 1.0)
