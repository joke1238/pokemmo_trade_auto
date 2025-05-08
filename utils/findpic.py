import cv2
import numpy as np
from houtai_pokemmo.utils.htscreenshot import WindowCapture
import matplotlib.pyplot as plt
from houtai_pokemmo.utils.window import FindHwnd
from houtai_pokemmo.Operate.mouse import  Virtual_Keyboard

class TemplateMatcher:
    def __init__(self, hwnd):
        """初始化模板匹配类"""

        self.window_capture = WindowCapture(hwnd)
        self.template = None
        self.background_color = None
        self.isShow = False
        self.matched_image = None

    def load_template(self, template_path):
        """加载模板图像"""
        self.template = None  # 清理之前的模板
        self.background_color = None  # 清理背景颜色

        self.template = cv2.imread(template_path)

        if self.template is None:
            raise ValueError(f"无法加载模板图像: {template_path}")

        self.background_color = self.get_background_color(self.template)
        # print(f"模板加载成功: {template_path}")

    def get_background_color(self, image):
        """获取图像的背景颜色（四个角的平均值）"""
        top_left = image[0, 0]
        top_right = image[0, -1]
        bottom_left = image[-1, 0]
        bottom_right = image[-1, -1]
        background_color = np.mean([top_left, top_right, bottom_left, bottom_right], axis=0)
        return background_color.astype(int)

    def preprocess_image(self, image, threshold=30):
        """预处理图像：去除背景颜色"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        lower_bound = np.array(self.background_color - threshold, dtype=np.uint8)
        upper_bound = np.array(self.background_color + threshold, dtype=np.uint8)
        mask = cv2.inRange(image, lower_bound, upper_bound)
        mask_inv = cv2.bitwise_not(mask)
        return cv2.bitwise_and(gray, gray, mask=mask_inv)

    def capture_screenshot(self):
        """截取屏幕指定区域"""
        screenshot = self.window_capture.capture(0 ,0)
        return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    def set_screenRect(self, region):
        """更新截图区域"""
        self.region = region

    def match_template(self, threshold=0.75):
        """执行模板匹配"""
        if self.template is None:
            raise ValueError("模板未加载。请使用 load_template 方法加载模板图像。")

        image = self.capture_screenshot()
        processed_image = self.preprocess_image(image)
        processed_template = self.preprocess_image(self.template)

        result = cv2.matchTemplate(processed_image, processed_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= threshold:
            h, w = processed_template.shape
            top_left = max_top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
            matched_position = (top_left[0] + w // 2, top_left[1] + h // 2)
            self.matched_image = image
            return matched_position
        else:
            return None

    def set_show(self, isShow):
        """设置是否显示匹配图像"""
        self.isShow = isShow

    def show_matched_image(self):
        """显示匹配到的图像"""
        if self.matched_image is not None and self.isShow:
            plt.imshow(cv2.cvtColor(self.matched_image, cv2.COLOR_BGR2RGB))
            plt.title("Matched Image")
            plt.axis('off')
            plt.show()
        else:
            # print("没有可显示的匹配结果，请先进行模板匹配。")
            pass

    def match_jy_template(self, threshold=0.8):
        """执行模板匹配"""
        if self.template is None:
            raise ValueError("模板未加载。请使用 load_template 方法加载模板图像。")

        image = self.capture_screenshot()  # 捕获截图
        processed_image = self.preprocess_image(image)  # 预处理截图
        processed_template = self.preprocess_image(self.template)  # 预处理模板

        # 执行模板匹配
        result = cv2.matchTemplate(processed_image, processed_template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        # 如果匹配度超过阈值
        if max_val >= threshold:
            h, w = processed_template.shape  # 获取模板的高宽
            top_left = max_loc  # 获取匹配区域的左上角坐标
            bottom_right = (top_left[0] + w, top_left[1] + h)  # 计算右下角坐标

            # 在图像上绘制矩形框（可以去除这部分如果不需要显示框）
            cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)

            self.matched_image = image  # 存储匹配后的图像

            # 返回左上角和右下角的坐标 (x1, y1, x2, y2)
            return top_left[0], top_left[1], bottom_right[0], bottom_right[1]
        else:
            return None  # 如果没有找到匹配

if __name__ == '__main__':
    _, hwnd = FindHwnd()
    vk = Virtual_Keyboard()
    tm = TemplateMatcher(hwnd)
    tm.set_show(True)
    tm.load_template('../pic/xuehua/img_15.png')
    while True:

        template = tm.match_template()
        if template:
            tm.show_matched_image()
            print(template)
            break
        else:
            continue
    # tm.show_matched_image()


