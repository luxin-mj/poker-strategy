import logging
import sys

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("poker_assistant.log")
    ]
)

from core.parser import HandHistoryParser
from core.strategy import StrategyEngine
from database.manager import DatabaseManager
import json

class PokerAssistant:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.parser = HandHistoryParser()
        self.strategy = StrategyEngine()
        self.db = DatabaseManager()
        self.logger.info("PokerAssistant initialized.")

    def process_message(self, message: str) -> dict:
        """处理单条消息"""
        try:
            self.logger.debug(f"Processing message: {message}")
            
            # 解析消息
            parsed = self.parser.parse_message(message)
            if not parsed:
                self.logger.error("消息解析失败")
                return {"status": "error", "message": "消息解析失败"}
            
            # 简单消息处理
            if parsed.get("type") == "round_change":
                game_state = {
                    "street": parsed.get("street"),
                    "pot": parsed.get("pot"),
                    "board": [str(card) for card in parsed.get("board", [])],
                    "hero_cards": [str(card) for card in parsed.get("hero_cards", [])],
                    "position": parsed.get("position")
                }

                # 更新对手行为数据
                for opponent in parsed.get("opponents", []):
                    self.db.update_opponent_stats(opponent["userId"], opponent["lastAction"], parsed.get("street"))

                # 获取对手统计数据
                opponent_stats = self.db.get_opponent_stats(parsed.get("opponentId"))

                # 获取策略建议
                advice = self.strategy.get_advice(game_state, opponent_stats)

                self.logger.info(f"Game State: {game_state}")
                self.logger.info(f"Advice: {advice}")

                return {
                    "status": "success",
                    "message_type": "round_change",
                    "game_state": game_state,
                    "advice": advice
                }

            return {
                "status": "success",
                "message_type": parsed.get("type"),
                "data": parsed
            }
            
        except Exception as e:
            self.logger.error(f"处理错误: {str(e)}", exc_info=True)
            return {"status": "error", "message": f"处理错误: {str(e)}"}

if __name__ == "__main__":
    assistant = PokerAssistant()
    print("德州扑克助手已启动")
    print("请输入游戏消息 (输入 'quit' 退出):")

    while True:
        try:
            message = input("\n> ")
            if message.lower() == 'quit':
                break

            result = assistant.process_message(message)
            print("\n分析结果:")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        except KeyboardInterrupt:
            print("\n程序已终止")
            break
        except Exception as e:
            print(f"\n错误: {e}")
