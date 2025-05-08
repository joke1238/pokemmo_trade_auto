import time
from ctypes import windll, byref, c_ubyte
from ctypes.wintypes import RECT
import numpy as np
import cv2
from houtai_pokemmo.utils.CheakTitle import find_similar_windows

class WindowCapture:
    def __init__(self, handle=None):
        '''
        初始化窗口截图类
        :param handle: 窗口句柄，如果为 None，会通过 find_similar_windows() 获取
        '''
        self.handle = handle



    def capture(self, x1=0, y1=0, x2=None, y2=None):
        '''
        捕获窗口截图
        :param x1, y1: 截图区域的左上角坐标
        :param x2, y2: 截图区域的右下角坐标
        :return: 返回截图的 NumPy 数组（BGRA 格式）
        '''
        # 加载 Windows API 函数
        GetDC = windll.user32.GetDC
        CreateCompatibleDC = windll.gdi32.CreateCompatibleDC
        GetClientRect = windll.user32.GetClientRect
        CreateCompatibleBitmap = windll.gdi32.CreateCompatibleBitmap
        SelectObject = windll.gdi32.SelectObject
        BitBlt = windll.gdi32.BitBlt
        SRCCOPY = 0x00CC0020
        GetBitmapBits = windll.gdi32.GetBitmapBits
        DeleteObject = windll.gdi32.DeleteObject
        ReleaseDC = windll.user32.ReleaseDC
        windll.user32.SetProcessDPIAware()

        # 获取窗口客户区域的尺寸
        r = RECT()
        GetClientRect(self.handle, byref(r))
        client_width, client_height = r.right, r.bottom

        # 如果没有传入 x2 或 y2，默认使用客户区域的大小
        if x2 is None:
            x2 = client_width
        if y2 is None:
            y2 = client_height

        # 获取窗口的设备上下文（DC）
        dc = GetDC(self.handle)
        cdc = CreateCompatibleDC(dc)
        bitmap = CreateCompatibleBitmap(dc, x2 - x1, y2 - y1)

        # 选择位图对象
        SelectObject(cdc, bitmap)

        # 使用 BitBlt 复制窗口内容到位图
        BitBlt(cdc, 0, 0, x2 - x1, y2 - y1, dc, x1, y1, SRCCOPY)

        # 获取位图的字节数据
        total_bytes = (x2 - x1) * (y2 - y1) * 4
        buffer = bytearray(total_bytes)
        byte_array = c_ubyte * total_bytes
        GetBitmapBits(bitmap, total_bytes, byte_array.from_buffer(buffer))

        # 清理资源
        DeleteObject(bitmap)
        DeleteObject(cdc)
        ReleaseDC(self.handle, dc)

        # 将字节数据转换为 NumPy 数组（BGRA 格式）
        return np.frombuffer(buffer, dtype=np.uint8).reshape(y2 - y1, x2 - x1, 4)

    def capture_screenshot(self, region, save_path):
        """
        截取窗口的部分区域并保存截图
        :param region: 截图区域 (x1, y1, x2, y2)
        :param save_path: 截图保存的路径
        :return: 截图的 BGR 格式图像
        """
        time.sleep(0.32)  # 等待窗口加载完成
        # 获取原始的截图
        screenshot = self.capture(region[0], region[1], region[2], region[3])  # 使用自定义区域

        # 转换为 RGB 格式（因为 pyautogui 使用的是 RGB，而非 BGRA）
        rgb_image = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2RGB)

        # 直接保存 RGB 图像
        cv2.imwrite(save_path, rgb_image)  # 将图像保存为文件

        return rgb_image  # 返回 RGB 格式图像
