import logging
from player import Player
from strategy import Strategy
import random

class Simulation:
    def __init__(self, db_manager):
        self.db = db_manager
        self.players = [Player(user_id, db_manager, is_user=(user_id == 0)) for user_id in range(6)]  # 玩家 0 为用户玩家
        self.strategy = Strategy()
        self.logger = logging.getLogger(self.__class__.__name__)

    def simulate_game(self, rounds=1):
        for round_number in range(1, rounds + 1):
            self.logger.info(f"第 {round_number} 轮开始。")
            game_state = self.get_game_state("preflop")
            self.deal_hands()
            self.log_preflop_state(game_state)
            self.play_round(game_state)
            
            # 翻牌圈
            game_state = self.get_game_state("flop")
            self.log_flop_state(game_state)
            self.play_round(game_state)
            
            # 转牌圈
            game_state = self.get_game_state("turn")
            self.log_turn_state(game_state)
            self.play_round(game_state)
            
            # 河牌圈
            game_state = self.get_game_state("river")
            self.log_river_state(game_state)
            self.play_round(game_state)
            
            self.summarize_chips()
            self.determine_winner()
            self.logger.info(f"第 {round_number} 轮结束。")

    def get_game_state(self, street):
        pot_size = sum(player.in_pot for player in self.players)  # 更新当前彩池大小
        community_cards = self.get_community_cards(street)
        return {
            "street": street,
            "pot_size": pot_size,
            "community_cards": community_cards
        }

    def get_community_cards(self, street):
        if street == "flop":
            return [(random.randint(2, 14), random.choice(['hearts', 'diamonds', 'clubs', 'spades'])) for _ in range(3)]
        elif street == "turn":
            return [(random.randint(2, 14), random.choice(['hearts', 'diamonds', 'clubs', 'spades'])) for _ in range(4)]
        elif street == "river":
            return [(random.randint(2, 14), random.choice(['hearts', 'diamonds', 'clubs', 'spades'])) for _ in range(5)]
        return []

    def deal_hands(self):
        for player in self.players:
            player.hand = [(random.randint(2, 14), random.choice(['hearts', 'diamonds', 'clubs', 'spades'])) for _ in range(2)]
            player.in_pot = 0  # 重置每个玩家的投入筹码
            self.logger.info(f"玩家 {player.user_id} (位置: {self.get_position(player.user_id)}) 的手牌: {player.hand}")

    def log_preflop_state(self, game_state):
        self.logger.info(f"翻前轮，当前底池 {game_state['pot_size']} BB")
        for player in self.players:
            self.logger.info(f"玩家 {player.user_id} (位置: {self.get_position(player.user_id)}) 的手牌: {player.hand}")

    def log_flop_state(self, game_state):
        if game_state['street'] == "flop":
            self.logger.info(f"翻牌圈，公共牌: {game_state['community_cards']}, 当前底池 {game_state['pot_size']} BB")

    def log_turn_state(self, game_state):
        if game_state['street'] == "turn":
            self.logger.info(f"转牌圈，公共牌: {game_state['community_cards']}, 当前底池 {game_state['pot_size']} BB")

    def log_river_state(self, game_state):
        if game_state['street'] == "river":
            self.logger.info(f"河牌圈，公共牌: {game_state['community_cards']}, 当前底池 {game_state['pot_size']} BB")

    def get_position(self, user_id):
        positions = ["BTN", "SB", "BB", "UTG", "MP", "CO"]
        return positions[user_id % len(positions)]

    def play_round(self, game_state):
        current_bet = 0
        while True:
            actions_taken = 0
            for player in self.players:
                if player.chips > 0:
                    opponent_stats = self.db.get_opponent_stats(player.user_id)
                    action = player.get_action(game_state, opponent_stats, self.strategy)
                    if action == "RAISE":
                        bet_amount = min(10, player.chips)  # 示例逻辑，RAISE 10 筹码或全部筹码
                        player.chips -= bet_amount
                        player.in_pot += bet_amount
                        current_bet = bet_amount
                        actions_taken += 1
                    elif action == "CALL":
                        call_amount = min(current_bet - player.in_pot, player.chips)
                        player.chips -= call_amount
                        player.in_pot += call_amount
                        actions_taken += 1
                    elif action == "ALL-IN":
                        all_in_amount = player.chips
                        player.chips = 0
                        player.in_pot += all_in_amount
                        actions_taken += 1
                    elif action == "FOLD":
                        player.in_pot = 0
                        continue
                    self.db.update_opponent_stats(player.user_id, action, game_state['street'])
                    self.logger.info(f"玩家 {player.user_id} (位置: {self.get_position(player.user_id)}) 进行了动作: {action}, 当前底池: {sum(p.in_pot for p in self.players)} BB")
                    self.update_strategy(player, game_state)
            active_players = [p for p in self.players if p.chips > 0]
            if len(active_players) == 1 or actions_taken == 0:
                break

    def update_strategy(self, player, game_state):
        opponent_stats = self.db.get_opponent_stats(player.user_id)
        self.logger.debug(f"更新玩家 {player.user_id} 的策略，基于当前状态 {game_state} 和对手统计 {opponent_stats}")

    def summarize_chips(self):
        self.logger.info("当前每位玩家的筹码情况：")
        for player in self.players:
            self.logger.info(f"玩家 {player.user_id} (位置: {self.get_position(player.user_id)}): {player.chips} 筹码")

    def determine_winner(self):
        active_players = [p for p in self.players if p.chips > 0 or p.in_pot > 0]
        if active_players:
            winner = random.choice(active_players)
            winning_hand = winner.hand
            self.logger.info(f"胜者是玩家 {winner.user_id} (位置: {self.get_position(winner.user_id)}), 获胜的手牌组合: {winning_hand}")
        self.logger.info("每位玩家的手牌组合和策略分析：")
        for player in self.players:
            self.logger.info(f"玩家 {player.user_id} (位置: {self.get_position(player.user_id)}), 手牌: {player.hand}, 筹码: {player.chips}")
