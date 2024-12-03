from core.parser import HandHistoryParser
from core.strategy import StrategyEngine
from database.manager import DatabaseManager
import json

class PokerAssistant:
    def __init__(self):
        self.parser = HandHistoryParser()
        self.strategy = StrategyEngine()
        self.db = DatabaseManager()
        
    def process_message(self, message: str) -> dict:
        """处理单条消息"""
        try:
            # 解析消息
            parsed = self.parser.parse_message(message)
            if not parsed:
                return {"status": "error", "message": "消息解析失败"}
            
            # 简单消息处理
            if parsed.get("type") == "round_change":
                game_state = {
                    "street": parsed.get("street"),
                    "pot": parsed.get("pot"),
                    "board": [str(card) for card in parsed.get("board", [])],
                    "hero_cards": [str(card) for card in parsed.get("hero_cards", [])]
                }
                
                # 获取策略建议
                advice = self.strategy.get_advice(game_state)
                
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
            import traceback
            print(traceback.format_exc())
            return {"status": "error", "message": f"处理错误: {str(e)}"}

def main():
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

if __name__ == "__main__":
    main()
