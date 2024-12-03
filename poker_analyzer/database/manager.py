import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path: str = 'poker_history.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """创建数据库表"""
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS hands (
                hand_id TEXT PRIMARY KEY,
                timestamp DATETIME,
                hero_id INTEGER,
                hero_position TEXT,
                hero_cards TEXT,
                board TEXT,
                final_pot REAL,
                result REAL
            );
            
            CREATE TABLE IF NOT EXISTS actions (
                hand_id TEXT,
                street TEXT,
                user_id INTEGER,
                position TEXT,
                action_type TEXT,
                amount REAL,
                pot_size REAL
            );
            
            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,
                nickname TEXT,
                total_hands INTEGER,
                vpip REAL,
                pfr REAL,
                wwsf REAL,
                last_updated DATETIME
            );
        ''')
        self.conn.commit()
