import win32gui
import difflib

def enum_windows_callback(hwnd, windows):
    """回调函数，枚举所有窗口并查找相似标题"""
    title = win32gui.GetWindowText(hwnd)
    "Pokemon Blaze Online"
    # 只匹配与目标标题长度相同的窗口
    if len(title) == len("PokeMMo") and is_similar(title, "PokeMMo"):
        windows.append(hwnd)  # 将符合条件的窗口句柄添加到列表

def is_similar(title, target):
    """判断窗口标题与目标字符串的相似性（通过编辑距离或模糊匹配）"""
    # 清理标题：去除多余的空格并将其转换为小写
    title_clean = title.strip().lower()
    target_clean = target.strip().lower()

    # 使用 difflib 库进行模糊匹配，返回相似度分数
    similarity = difflib.SequenceMatcher(None, title_clean, target_clean).ratio()

    # 如果相似度大于0.6，认为是相似窗口
    return similarity >= 0.4

def find_similar_windows():
    """查找标题相似且长度与目标标题相同的窗口"""
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)  # 枚举所有窗口
    return windows

# 使用示例
if __name__ == '__main__':
    similar_windows = find_similar_windows()
    if similar_windows:
        for hwnd in similar_windows:
            title = win32gui.GetWindowText(hwnd)
            print(f'找到窗口句柄: {hwnd}，窗口标题: {title}')
    else:
        print("没有找到类似的窗口")
