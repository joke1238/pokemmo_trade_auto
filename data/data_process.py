import json
from enum import Enum
from houtai_pokemmo.data.req import get_pokemon_data
from houtai_pokemmo.config import excluded_terms

class Level(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

def price(item_price):
    if item_price < 1000:
        return item_price - 100
    if item_price > 500000:
        return item_price - 25000
    return item_price * 0.95

class MarketDataProcessor:
    @staticmethod
    def fetch_market_data():
        try:
            return get_pokemon_data().json()["data"]
        except Exception as e:
            print(f"[错误] 获取市场数据失败: {e}")
            return []

    @staticmethod
    def process(save_to_file=True, return_data=False, filename='new_data.json',textEdit=None):
        textEdit.append("正在获取市场数据...")
        raw_data = MarketDataProcessor.fetch_market_data()
        new_data = {}

        for item in raw_data:
            try:
                item_id = item["i"]["i"]
                item_name = item["i"]["n"]["en"]
                item_data = item["i"]["d"]["en"]
                item_num = item["q"]

                if any(term in item_name for term in excluded_terms):
                    item_price = 0
                else:
                    item_price = price(item["p"])

                if item_num < 20:
                    distribute = Level.LOW.value
                elif item_num < 50:
                    distribute = Level.MEDIUM.value
                else:
                    distribute = Level.HIGH.value

                new_data[item_name] = {
                    "id": item_id,
                    "name": item_name,
                    "data": item_data,
                    "price": item_price,
                    "num": item_num,
                    "distribute": distribute
                }
            except Exception as e:
                print(f"[跳过] 处理物品时出错: {e}")

        if save_to_file:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(new_data, f, ensure_ascii=False, indent=4)
                textEdit.append(f"✅ 数据已写入 {filename} 文件。")
                print(f"✅ 数据已写入 {filename} 文件。")
            except Exception as e:
                print(f"[错误] 写入文件失败: {e}")
                textEdit.append(f"[错误] 写入文件失败: {e}")

        if return_data:
            return new_data
