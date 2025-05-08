import json
import time
import os
from PySide6.QtGui import QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox, QVBoxLayout, QPushButton, QLabel, QDialog, QSpinBox,QDoubleSpinBox
from houtai_pokemmo.Func.jyh import Houtai_Pokemmo
from houtai_pokemmo import config
from houtai_pokemmo.utils.rule import get_rule
from winsound import PlaySound, SND_FILENAME
from houtai_pokemmo.data.data_process import MarketDataProcessor
def calculate_profit(quantity, sell_price, buy_price):
    fee_per_item = max(min(int(sell_price * 0.025), 25000), 100)
    total_fee = fee_per_item * quantity
    profit = quantity * sell_price - quantity * buy_price - total_fee
    return profit

def get_resource_path(relative_path):
    """获取资源文件路径，支持打包后运行"""
    return os.path.join(os.path.abspath("."), relative_path)

class WorkerThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(int)

    def __init__(self, n):
        super().__init__()
        try:
            self.n = int(n)
            self._running = True
        except ValueError:
            QMessageBox.warning(None, "警告", "请输入有效的数字！")

    def stop(self):
        self._running = False

    def run(self):
        rules = {}
        with open(get_resource_path(R"data\rule_config.json"), 'r', encoding='utf-8') as f:
            rules = json.load(f)
        self.log_signal.emit(f"运行 {self.n} 分钟后关闭脚本")
        excluded_terms = config.excluded_terms
        shutdown_time = time.time() + self.n * 60
        total_profit = 0
        jyh = Houtai_Pokemmo()
        price_list = jyh.load_price_list(get_resource_path(R"data\new_data.json"))
        remainder_money = int(jyh.capture_and_money())
        self.log_signal.emit(f"当前余额：{remainder_money}")
        jyh.tm.load_template(get_resource_path(R"Func\pic\jyh\date.png"))
        while time.time() < shutdown_time and self._running:
            coordinates = jyh.fetch_coordinates()
            if coordinates:
                extracted_text_list = jyh.capture_and_extract_text(coordinates)
                print(extracted_text_list)
                parsed_list = jyh.parse_item_string(extracted_text_list)

                if parsed_list:
                    item_name, item_quantity, item_price = parsed_list[0], parsed_list[1], parsed_list[2]
                    print(item_name.replace('\n', ' '), item_quantity, item_price)
                    if any(term in item_name for term in excluded_terms):
                        jyh.click_flush()
                        continue

                    in_dict = jyh.fuzzy_search_in_dict(item_name, price_list)
                    if in_dict:
                        matched_item = next(iter(in_dict))
                        price = in_dict[matched_item]['price']
                        distribute = in_dict[matched_item]['distribute']

                        if get_rule(float(price), float(item_price), int(item_quantity), int(distribute),rules):
                            jyh.click_buy()
                            if int(item_quantity) > 1 and remainder_money >= int(item_price) * int(item_quantity):
                                jyh.click_all()
                                jyh.click_Accept()
                                jyh.key_yes()
                                remainder_money -= int(item_price) * int(item_quantity)
                            else:

                                jyh.key_yes()
                                remainder_money -= int(item_price)
                                item_quantity = 1

                            Flag = jyh.check_buy()
                            if Flag == 1:
                                profit = calculate_profit(int(item_quantity), int(price), int(item_price))
                                total_profit += profit

                                PlaySound('coin-.wav',
                                                   SND_FILENAME)

                                self.log_signal.emit(f"✅ 购买成功：{item_name} x{item_quantity}，价格：{item_price}")
                                self.log_signal.emit(f"物品信息：{matched_item}，价格：{price}，分发：{distribute}")
                                self.log_signal.emit(f"预计赚取：{profit}")
                                self.log_signal.emit(f"当前余额：{remainder_money}\n")
                                with open("jyh_success_log.txt", 'a', encoding='utf-8') as f:
                                    f.write(
                                        f"{item_name} x{item_quantity}，价格：{item_price}，利润：{profit}，市场价：{price}，分发：{distribute}\n")
                            else:
                                self.log_signal.emit(f"❌ 购买失败：{item_name} x{item_quantity}，价格：{item_price}")
                                self.log_signal.emit(f"物品信息：{matched_item}，价格：{price}，分发：{distribute}")
                                with open("jyh_buy_failed_data.txt", 'a', encoding='utf-8') as f:
                                    f.write(
                                        f"{item_name} x{item_quantity}，价格：{item_price}，物品信息：{matched_item}，价格：{price}，分发：{distribute}\n")
                                remainder_money += int(item_price) * int(item_quantity)

                            if remainder_money < 10000:
                                self.log_signal.emit("💰 余额不足，退出脚本")
                                break

                            jyh.click_flush()
                        else:
                            self.log_signal.emit(
                                f"⏩ 跳过：{item_name} 不符合捡漏规则，市场价：{price}，售价：{item_price}，数量：{item_quantity}，分发：{distribute}")
                            # with open("jyh_rule_skipped_log.txt", 'a', encoding='utf-8') as f:
                            #     f.write(
                            #         f"{item_name} x{item_quantity}，售价：{item_price}，市场价：{price}，分发：{distribute}\n")
                            jyh.click_flush()
                    else:
                        self.log_signal.emit(f"❓ 跳过：未在市场数据中找到 {item_name}")
                        with open("jyh_no_match_log.txt", 'a', encoding='utf-8') as f:
                            f.write(f"{item_name} x{item_quantity}，售价：{item_price}\n")
                        jyh.click_flush()
                else:
                    jyh.click_flush()
            else:
                self.log_signal.emit("❌ GUI 未找到，脚本退出")
                break

        self.log_signal.emit(f"脚本已关闭，当前余额：{remainder_money}")
        self.log_signal.emit(f"💹 本次累计预计利润：{total_profit} 金币")
        self.finished_signal.emit(total_profit)

class RuleEditorDialog(QDialog):
    def __init__(self, json_path=get_resource_path("data/rule_config.json")):
        super().__init__()
        self.setWindowTitle("规则设置编辑器")
        self.json_path = get_resource_path(json_path)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.inputs = {}  # 存放每个字段的 QSpinBox 或 QDoubleSpinBox
        self.load_config()
        self.add_confirm_button()

    def load_config(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "加载失败", f"无法加载配置文件: {e}")
            self.config = {}

        for key, value in self.config.items():
            self.layout.addWidget(QLabel(f"【{key}】"))
            if isinstance(value, dict) and all(isinstance(v, dict) for v in value.values()):  # distribute_3
                for subkey, subvalue in value.items():
                    self.add_rule_input(f"{key}_{subkey}", subvalue)
            else:
                self.add_rule_input(key, value)

    def add_rule_input(self, label, rule_dict):
        price_ratio_box = QDoubleSpinBox()
        price_ratio_box.setRange(0, 1)
        price_ratio_box.setSingleStep(0.01)
        price_ratio_box.setValue(rule_dict.get("price_ratio", 0.5))

        min_profit_box = QSpinBox()
        min_profit_box.setRange(0, 10_000_000)
        min_profit_box.setValue(rule_dict.get("min_profit", 0))

        row = QVBoxLayout()
        row.addWidget(QLabel(f"{label}：价格比例"))
        row.addWidget(price_ratio_box)
        row.addWidget(QLabel("最低利润"))
        row.addWidget(min_profit_box)

        self.layout.addLayout(row)
        self.inputs[label] = (price_ratio_box, min_profit_box)

    def add_confirm_button(self):
        btn = QPushButton("保存配置")
        btn.clicked.connect(self.save_config)
        self.layout.addWidget(btn)

    def save_config(self):
        new_config = {
            "distribute_1": {},
            "distribute_2": {},
            "distribute_3": {
                "≤5000": {}, "5000~20000": {}, "20000~50000": {}, "≥50000": {}
            }
        }
        for key, (ratio_box, profit_box) in self.inputs.items():
            if key.startswith("distribute_3_"):
                subkey = key.split("_", 2)[2]
                new_config["distribute_3"][subkey] = {
                    "price_ratio": ratio_box.value(),
                    "min_profit": profit_box.value()
                }
            else:
                new_config[key] = {
                    "price_ratio": ratio_box.value(),
                    "min_profit": profit_box.value()
                }

        try:
            with open(self.json_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            QMessageBox.information(self, "保存成功", "规则配置已保存。")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"写入失败：{e}")

class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("规则设置")
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("设置运行时长（分钟）："))
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 120)
        self.layout.addWidget(self.time_input)
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.accept)
        self.layout.addWidget(self.confirm_btn)
        self.setLayout(self.layout)


class Jyh_Bot_Ui(QWidget):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.Mian_ui = loader.load("Main.ui")
        self.Mian_ui.setWindowTitle("JYH 自动购买脚本 -- 3.0.0")
        self.Mian_ui.setWindowIcon(QIcon("狼人黄昏形态-48.ico"))

        self.Mian_ui.show()
        self.Mian_ui.textEdit.setReadOnly(True)
        self.Mian_ui.textEdit.append("测试文本：UI 加载成功")

        self.start_ui = loader.load("start.ui")
        self.start_ui.setWindowTitle("JYH 自动购买脚本")
        self.start_ui.setWindowIcon(QIcon("狼人黄昏形态-48.ico"))
        self.Mian_ui.doubleSpinBox.setValue(Houtai_Pokemmo.flush_timeout)
        self.Mian_ui.show()
        self.Mian_ui.pushButton.clicked.connect(self.show_settings_dialog)
        self.Mian_ui.pushButton_2.clicked.connect(self.stop_worker)
        self.Mian_ui.pushButton_3.clicked.connect(self.show_log_ui)
        self.Mian_ui.pushButton_4.clicked.connect(self.updata_data)
        self.Mian_ui.pushButton_5.clicked.connect(self.show_rule_editor)
        self.Mian_ui.pushButton_6.clicked.connect(self.set_mode1)
        self.Mian_ui.pushButton_7.clicked.connect(self.set_mode2)

        self.log_ui = loader.load("log.ui")
        self.log_ui.setWindowTitle("JYH 自动购买脚本-日志")
        self.log_ui.textEdit.setReadOnly(True)
        self.log_ui.setWindowIcon(QIcon("狼人黄昏形态-48.ico"))
    def set_mode1(self):
        Houtai_Pokemmo.mode = 1
        self.Mian_ui.textEdit.append("模式切换为1")
    def set_mode2(self):
        Houtai_Pokemmo.mode = 2
        self.Mian_ui.textEdit.append("模式切换为2")
    def show_rule_editor(self):
        dialog = RuleEditorDialog()
        dialog.exec()

    def updata_data(self):
        MarketDataProcessor.process(save_to_file=True, return_data=False, filename=get_resource_path(R"data\new_data.json"),textEdit=self.Mian_ui.textEdit)
    def show_settings_dialog(self):
        Houtai_Pokemmo.flush_timeout = self.Mian_ui.doubleSpinBox.value()
        dialog = SettingsDialog()
        if dialog.exec():
            minutes = dialog.time_input.value()
            self.start_ui.close()
            self.worker = WorkerThread(minutes)
            self.worker.log_signal.connect(self.update_text)
            self.worker.start()
    def show_log_ui(self):
        self.log_ui.show()
    def stop_worker(self):
        if hasattr(self, 'worker'):
            self.worker.stop()
            self.update_text("🛑 手动停止脚本...")

    def update_text(self, msg):
        self.append_log_all(msg)
        self.append_log_success_only(msg)

    def append_log_all(self, msg: str):
        """主窗口显示所有日志"""
        if hasattr(self.Mian_ui, "textEdit"):
            self.Mian_ui.textEdit.append(msg)

    def append_log_success_only(self, msg: str):
        """日志窗口仅记录购买成功的内容"""
        if hasattr(self.log_ui, "textEdit") and (
                msg.startswith("✅ 购买成功：") or
                msg.startswith("物品信息：") or
                msg.startswith("预计赚取：") or
                msg.startswith("❌ 购买失败：")
        ):
            self.log_ui.textEdit.append(msg)


if __name__ == '__main__':
    app = QApplication([])
    window = Jyh_Bot_Ui()
    app.exec()