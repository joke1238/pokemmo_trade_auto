import win32gui
from houtai_pokemmo.utils.CheakTitle import find_similar_windows

def get_window_rect(hwnd):
    """根据窗口句柄获取窗口的矩形坐标 (left, top, width, height)"""
    if not win32gui.IsWindow(hwnd):
        raise ValueError(f"无效的窗口句柄: {hwnd}")
    rect = win32gui.GetWindowRect(hwnd)
    left, top, right, bottom = rect
    width = right - left
    height = bottom - top
    return (left, top, width, height)

def FindHwnd():
    """根据窗口标题查找窗口并获取其矩形坐标"""
    hwnds = find_similar_windows()  # 自动匹配窗口标题
    if hwnds:  # 如果找到了窗口
        hwnd = hwnds[0]  # 取第一个找到的窗口句柄
        rect = get_window_rect(hwnd)  # 根据找到的句柄获取矩形坐标
        return rect, hwnd
    else:
        print(f"未找到与 'PokeOne' 相似的窗口")
        return None

def resize_window(hwnd, width, height):
    """调整窗口大小"""
    if win32gui.IsWindow(hwnd):
        rect = get_window_rect(hwnd)
        left, top = rect[0], rect[1]
        win32gui.MoveWindow(hwnd, left, top, width, height, True)
    else:
        raise ValueError(f"无效的窗口句柄: {hwnd}")

if __name__ == '__main__':
    result = FindHwnd()
    print(result)
    if result is not None:  # 检查返回值是否为 None
        rect, hwnd = result
        print("找到窗口，当前坐标：", rect)
        # 修改窗口大小，例如设置宽度为800，高度为600
        resize_window(hwnd, 800, 600)
        print("窗口已调整大小")
