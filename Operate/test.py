import time
import win32api
import win32con
import win32gui
from houtai_pokemmo.utils.window import FindHwnd


class Virtual_Keyboard(object):

    def __init__(self):
        _, self.hwnd = FindHwnd()
        self.hwnd_title = win32gui.GetWindowText(self.hwnd)
        # win32gui.SetForegroundWindow(self.hwnd)  # 激活窗口
        print(f"窗口句柄: {self.hwnd}, 窗口标题: {self.hwnd_title}")

        self.vlaue_key = {
            "A": "65",
            "B": "66",
            "C": "67",
            "D": "68",
            "E": "69",
            "F": "70",
            "G": "71",
            "H": "72",
            "I": "73",
            "J": "74",
            "K": "75",
            "L": "76",
            "M": "77",
            "N": "78",
            "O": "79",
            "P": "80",
            "Q": "81",
            "R": "82",
            "S": "83",
            "T": "84",
            "U": "85",
            "V": "86",
            "W": "87",
            "X": "88",
            "Y": "89",
            "Z": "90",
            "0": "48",
            "1": "49",
            "2": "50",
            "3": "51",
            "4": "52",
            "5": "53",
            "6": "54",
            "7": "55",
            "8": "56",
            "9": "57",
            "F1": "112",
            "F2": "113",
            "F3": "114",
            "F4": "115",
            "F5": "116",
            "F6": "117",
            "F7": "118",
            "F8": "119",
            "F9": "120",
            "F10": "121",
            "F11": "122",
            "F12": "123",
            "TAB": "9",
            "ALT": "18",
            "ENTER": "13"
        }

    # 模拟一次按键的输入，间隔值默认0.1S
    def key_press(self, key: str, interval=0.1):
        key = key.upper()
        key_num = int(self.vlaue_key[key])
        num = win32api.MapVirtualKey(key_num, 0)
        dparam = 1 | (num << 16)
        uparam = 1 | (num << 16) | (1 << 30) | (1 << 31)

        # 激活窗口后发送消息
        # win32gui.SetForegroundWindow(self.hwnd)
        win32api.SendMessage(self.hwnd, win32con.WM_KEYDOWN, None, dparam)
        time.sleep(interval)
        win32api.SendMessage(self.hwnd, win32con.WM_KEYUP, None, uparam)

    # 模拟一个按键的按下
    def key_down(self, key: str):
        key = key.upper()
        key_num = int(self.vlaue_key[key])
        num1 = win32api.MapVirtualKey(key_num, 0)
        dparam = 1 | (num1 << 16)
        win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, None, dparam)

    # 模拟一个按键的弹起
    def key_up(self, key: str):
        key = key.upper()
        key_num = int(self.vlaue_key[key])
        num1 = win32api.MapVirtualKey(key_num, 0)
        uparam = 1 | (num1 << 16) | (1 << 30) | (1 << 31)
        win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, None, uparam)

    # 模拟鼠标的移动
    def mouse_move(self, x, y):
        x = int(x)
        y = int(y)
        point = win32api.MAKELONG(x, y)
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, None, point)

    # 模拟鼠标的按键抬起
    def mouse_up(self, x, y, button="L"):
        x = int(x)
        y = int(y)
        button = button.upper()
        point = win32api.MAKELONG(x, y)
        if button == "L":
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)
        elif button == "R":
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONUP, win32con.MK_RBUTTON, point)

    # 模拟鼠标的按键按下
    def mouse_down(self, x, y, button="L"):
        x = int(x)
        y = int(y)
        button = button.lower()
        point = win32api.MAKELONG(x, y)
        if button == "L":
            win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        elif button == "R":
            win32api.SendMessage(self.hwnd, win32con.WM_RBUTTONDOWN, win32con.MK_RBUTTON, point)

    # 模拟鼠标的左键双击
    def mouse_double(self, x, y):
        x = int(x)
        y = int(y)
        point = win32api.MAKELONG(x, y)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)

    # 模拟鼠标移动到坐标，并进行左键单击
    def mouse_move_press(self, x, y):
        x = int(x)
        y = int(y)
        point = win32api.MAKELONG(x, y)
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, None, point)
        time.sleep(0.2)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)

    # 模拟鼠标移动到坐标，并进行左键双击
    def mouse_move_press_double(self, x, y):
        x = int(x)
        y = int(y)
        point = win32api.MAKELONG(x, y)
        win32api.SendMessage(self.hwnd, win32con.WM_MOUSEMOVE, None, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, point)
        win32api.SendMessage(self.hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, point)


if __name__ == '__main__':
    keyboard = Virtual_Keyboard()


    keyboard.key_press("E")
