class Strategy:
    def suggest_action(self, player, game_state, opponent_stats):
        street = game_state['street']
        if street == "preflop":
            return self.preflop_strategy(player, opponent_stats)
        elif street == "flop":
            return self.flop_strategy(player, game_state, opponent_stats)
        elif street == "turn":
            return self.turn_strategy(player, game_state, opponent_stats)
        elif street == "river":
            return self.river_strategy(player, game_state, opponent_stats)
        return "FOLD"

    def preflop_strategy(self, player, opponent_stats):
        # 根据手牌强度和对手统计来决定动作
        hand = player.hand
        pair = hand[0][0] == hand[1][0]
        high_cards = [card[0] for card in hand if card[0] >= 10]
        suited = hand[0][1] == hand[1][1]

        # 如果对手是非常松的玩家，可以加大我们偷盲的频率
        if opponent_stats.get('PFR', 0) < 0.1:
            return "RAISE"

        if pair or suited and len(high_cards) == 2:
            return "RAISE"
        elif len(high_cards) == 1:
            return "CALL"
        else:
            return "FOLD"

    def flop_strategy(self, player, game_state, opponent_stats):
        # 根据公共牌和对手数据分析策略
        hand = player.hand
        community_cards = game_state['community_cards']
        all_cards = hand + community_cards

        if self.has_strong_hand(all_cards):
            return "RAISE"
        elif self.has_draw_potential(all_cards):
            return "CALL"
        else:
            # 如果对手的弃牌频率高，可以尝试半诈唬
            if opponent_stats.get('fold_frequency', 0) > 0.6:
                return "RAISE"
            return "FOLD"

    # 其他策略逻辑（如 turn 和 river）保持类似风格，结合手牌、公共牌和对手信息制定策略

    def has_strong_hand(self, cards):
        # 判断是否有强牌，如三条、顺子、同花、葫芦等
        return self.has_three_of_a_kind(cards) or self.has_straight(cards) or self.has_flush(cards) or self.has_full_house(cards)

    # 其他辅助函数同样可以保留或增加更多的手牌评估逻辑
