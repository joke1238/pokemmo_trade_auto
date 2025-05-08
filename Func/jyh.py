import difflib
import json
import os
import re
import time
import cv2
import numpy as np
import pytesseract
import win32con
import win32gui
from PIL import Image

from houtai_pokemmo.utils.findpic import TemplateMatcher
from houtai_pokemmo.utils.window import FindHwnd
from houtai_pokemmo.Operate.mouse import Virtual_Keyboard
from houtai_pokemmo.utils.htscreenshot import WindowCapture



def get_resource_path(relative_path):
    """获取资源文件路径，支持打包后运行"""
    return os.path.join(os.path.abspath("."), relative_path)


class Houtai_Pokemmo:
    flush_timeout = 0.1
    mode = 1
    def __init__(self):
        self.rect, self.hwnd = FindHwnd()
        self.vk = Virtual_Keyboard()
        self.tm = TemplateMatcher(self.hwnd)
        self.window_capture = WindowCapture(self.hwnd)


    def fetch_coordinates(self):
        coordinates = self.tm.match_jy_template(0.7)
        return coordinates

    def capture_and_money(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\money.png"))
        coordinates = self.tm.match_jy_template()
        region = (coordinates[0]+27, coordinates[1], coordinates[2]+80, coordinates[3])
        screenshot_path = get_resource_path(r"Func\pic\jyh\money_data.png")
        self.window_capture.capture_screenshot(region, screenshot_path)
        extracted_text = self.extract_text_from_image(screenshot_path)
        return re.sub(r'[^0-9]', '', extracted_text)

    def capture_and_extract_text(self, coordinates):
        region = (coordinates[0], coordinates[1] + 37, coordinates[2], coordinates[3] + 37)
        screenshot_path = get_resource_path(r"Func\pic\jyh\data.png")
        self.window_capture.capture_screenshot(region, screenshot_path)
        image = Image.open(screenshot_path)
        if Houtai_Pokemmo.mode == 1:

            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            crop_coords = [
                (0, 0, 223, 41),
                (223, 0, 63, 41),
                (286, 0, 106, 41)
            ]

            texts = []
            for x, y, w, h in crop_coords:
                cropped = image_cv[y:y + h, x:x + w]
                text = self.extract_text_from_cv_image(cropped)
                texts.append(text)

            return texts
        if Houtai_Pokemmo.mode == 2:
            text = self.extract_text_from_image(screenshot_path)
            match = re.match(r"(.+?)\s+(\d+)\s+\$(\d[\d,]*)", text)
            if match:
                name = match.group(1)  # EXP Candy (M)
                quantity = int(match.group(2))  # 7
                price = match.group(3)  # 3,333
                print(name, quantity, f"${price}")
                return [name, quantity, price]
            else:
                print("匹配失败")
                return ["", "", ""]




    def extract_text_from_cv_image(self, img):
        # 放大
        img = cv2.resize(img, (int(img.shape[1] * 1.5), int(img.shape[0] * 1.5)), interpolation=cv2.INTER_CUBIC)
        # 灰度、降噪
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        # OCR
        config = r'--oem 3 --psm 7'
        return pytesseract.image_to_string(denoised, config=config)

    def extract_text_from_image(self, image_path):
        # 读取图像
        img = cv2.imread(image_path)

        # 步骤 1：放大图像，提升识别率
        scale_percent = 125  # 放大 150%
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_CUBIC)

        # 步骤 2：转灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 步骤 3：降噪
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)

        # 步骤 5：OCR识别
        custom_config = r'--oem 3 --psm 6'

        text = pytesseract.image_to_string(denoised, config=custom_config)

        return text

    def clean_ocr_text(self, text):
        corrections = {
            "SOORP": "500RP",
            "SOOR": "500R",
            "LOO": "100",
            "‘": "",
        }
        for wrong, right in corrections.items():
            text = text.replace(wrong, right)
        return text

    def click_flush(self):
        if Houtai_Pokemmo.mode == 2:
            time.sleep(Houtai_Pokemmo.flush_timeout)
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\shuaxing.png"))
        coordinates = self.tm.match_template(0.6)
        if coordinates:
            self.vk.mouse_move_press(coordinates[0], coordinates[1])
        else:
            print("没有找到flush按钮")
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))

    def click_all(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\all.png"))
        while True:
            coordinates = self.tm.match_template()
            if coordinates:
                self.vk.mouse_move_press(coordinates[0], coordinates[1])
                break
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))

    def click_buy(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\buy.png"))
        coordinates = self.tm.match_template(0.6)
        self.vk.mouse_move_press(coordinates[0] + 62, coordinates[1] + 37)
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))

    def check_buy_fail(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\notfound.png"))
        coordinates = self.tm.match_template()
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))
        if coordinates:
            print("被抢光了")
            return True
        return False

    def check_not_enough_money(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\not_enough_money.png"))
        coordinates = self.tm.match_template()
        return bool(coordinates)

    def check_buy_success(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\buy_success.png"))
        coordinates = self.tm.match_template()
        return bool(coordinates)

    def check_buy(self):
        while True:
            if self.check_buy_success():
                return 1
            if self.check_buy_fail() or self.check_not_enough_money():
                return 0

    def key_yes(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\yes.png"))
        while True:
            if self.tm.match_template(0.4):
                break
        self.vk.key_press("ENTER", 0.01)
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))

    def click_Accept(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\Accept.png"))
        while True:
            coordinate = self.tm.match_template(0.4)
            if coordinate:
                self.vk.mouse_move_press(coordinate[0], coordinate[1])
                break
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\date.png"))

    def is_valid_price_string(self, s):
        pattern = r'^\$?\d{1,3}(,\d{3})*$'
        return bool(re.match(pattern, s))

    def parse_item_string(self, item_string):
        item_name, quantity, cleaned_price = item_string[0], item_string[1], item_string[2]
        if item_name == ""  or cleaned_price == "":
            return []
        cleaned_price = cleaned_price.replace('$', '').replace(',', '')
        try:
            quantity = int(quantity)

        except ValueError:
            quantity = 1

        try:
            cleaned_price = int(cleaned_price)
        except ValueError:
            return []
        return [item_name, quantity, cleaned_price]

    def load_price_list(self, price_list_path):
        with open(price_list_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def fuzzy_search_in_dict(self, search_key, dictionary, n=1, cutoff=0.9):
        close_matches = difflib.get_close_matches(search_key, dictionary.keys(), n=n, cutoff=cutoff)
        results = {match: dictionary[match] for match in close_matches}
        if results:
            sorted_results = sorted(results.items(), key=lambda x: x[1].get('price', 0))
            best_match = sorted_results[0]
            return {best_match[0]: best_match[1]}
        return {}

    def wait_for_loading(self):
        self.tm.load_template(get_resource_path(r"Func\pic\jyh\load.png"))
        while True:
            if self.tm.match_template():
                break

    def close_window(self):
        try:
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)
            print("窗口已关闭")
        except Exception as e:
            print(f"关闭窗口失败: {e}")


if __name__ == '__main__':
    houtai_pokemmo1 = Houtai_Pokemmo()
    houtai_pokemmo2 = Houtai_Pokemmo()
    print(houtai_pokemmo1.mode)
    print(houtai_pokemmo2.mode)
    Houtai_Pokemmo.mode = 2
    print(houtai_pokemmo1.mode)
    print(houtai_pokemmo2.mode)