import random
import logging

class Player:
    def __init__(self, user_id, db_manager, is_user=False):
        self.user_id = user_id
        self.db = db_manager
        self.is_user = is_user
        self.hand = []
        self.chips = 100  # 初始筹码数量
        self.in_pot = 0  # 当前轮次投入的筹码
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_action(self, game_state, opponent_stats, strategy):
        if self.is_user:
            # 根据游戏状态和对手的行为给出建议动作
            action = strategy.suggest_action(self, game_state, opponent_stats)
            self.logger.info(f"玩家 {self.user_id} (你) 的手牌: {self.hand}, 当前轮次: {game_state['street']}, 彩池大小: {game_state['pot_size']} BB, 建议动作: {action}")
        else:
            actions = ["FOLD", "CALL", "RAISE", "ALL-IN"]
            action = random.choice(actions)
        self.logger.debug(f"玩家 {self.user_id} 选择的动作: {action}")
        return action
