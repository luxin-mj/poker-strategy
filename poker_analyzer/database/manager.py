import sqlite3
import logging

class DatabaseManager:
    def __init__(self, db_path="poker_history.db"):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS opponents (
                    user_id INTEGER PRIMARY KEY,
                    vpip REAL DEFAULT 0.0,  -- 自愿入池百分比
                    pfr REAL DEFAULT 0.0,   -- 翻牌前加注百分比
                    hands_played INTEGER DEFAULT 0,
                    hands_raised INTEGER DEFAULT 0,
                    vpip_count INTEGER DEFAULT 0  -- 自愿入池次数
                )
            """)
            self.logger.info("Database table 'opponents' created or verified.")

    def update_opponent_stats(self, user_id, action, street):
        """更新对手的行为统计数据
        """
        with self.conn:
            cursor = self.conn.cursor()

            # Check if opponent exists, if not, create a new record
            cursor.execute("SELECT * FROM opponents WHERE user_id = ?", (user_id,))
            opponent = cursor.fetchone()

            if opponent is None:
                cursor.execute("INSERT INTO opponents (user_id) VALUES (?)", (user_id,))
                self.logger.info(f"Added new opponent with user_id: {user_id}")

            # Update statistics based on action
            if action in ["CALL", "BET", "RAISE"]:
                cursor.execute("UPDATE opponents SET vpip_count = vpip_count + 1 WHERE user_id = ?", (user_id,))
                self.logger.debug(f"VPIP incremented for user_id {user_id}.")

            if action == "RAISE" and street == "preflop":
                cursor.execute("UPDATE opponents SET hands_raised = hands_raised + 1 WHERE user_id = ?", (user_id,))
                self.logger.debug(f"Hands raised incremented for user_id {user_id}.")

            # Update the number of hands played
            cursor.execute("UPDATE opponents SET hands_played = hands_played + 1 WHERE user_id = ?", (user_id,))
            self.logger.debug(f"Hands played incremented for user_id {user_id}.")

            # Log raw counts before calculating rates
            opponent_stats_before = self.get_opponent_stats(user_id)
            self.logger.debug(f"Raw counts for user_id {user_id} before updating rates: {opponent_stats_before}")

            # Update VPIP and PFR based on updated statistics
            hands_played = opponent_stats_before['hands_played']
            hands_raised = opponent_stats_before['hands_raised']
            vpip_count = opponent_stats_before['vpip_count']

            self.logger.debug(f"Calculating VPIP and PFR for user_id {user_id}: hands_played={hands_played}, hands_raised={hands_raised}, vpip_count={vpip_count}")

            vpip_rate = (vpip_count / hands_played) if hands_played > 0 else 0
            pfr_rate = (hands_raised / hands_played) if hands_played > 0 else 0

            self.logger.debug(f"Updated rates for user_id {user_id}: VPIP={vpip_rate}, PFR={pfr_rate}")

            cursor.execute("""
                UPDATE opponents
                SET vpip = ?,
                    pfr = ?
                WHERE user_id = ?
            """, (vpip_rate, pfr_rate, user_id))

            # Log updated opponent statistics
            updated_opponent = self.get_opponent_stats(user_id)
            self.logger.debug(f"Updated opponent stats for user_id {user_id}: {updated_opponent}")

    def get_opponent_stats(self, user_id):
        """获取对手的行为统计数据
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, vpip, pfr, hands_played, hands_raised, vpip_count FROM opponents WHERE user_id = ?", (user_id,))
        opponent = cursor.fetchone()

        if opponent:
            return {
                "user_id": opponent[0],
                "vpip": opponent[1],
                "pfr": opponent[2],
                "hands_played": opponent[3],
                "hands_raised": opponent[4],
                "vpip_count": opponent[5]
            }
        else:
            return None

if __name__ == "__main__":
    # 设置日志配置
    logging.basicConfig(
        level=logging.DEBUG,  # 记录 DEBUG 级别及以上的所有日志
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()  # 输出到控制台
        ]
    )

    # 示例初始化
    db_manager = DatabaseManager()
    db_manager.update_opponent_stats(user_id=1, action="RAISE", street="preflop")
    db_manager.update_opponent_stats(user_id=1, action="CALL", street="flop")
    stats = db_manager.get_opponent_stats(user_id=1)
    print(stats)
