import cv2
import pytesseract
import numpy as np


def extract_text_from_image(image_path):
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


# 示例调用
image_path = r'D:\pythonPokemmo-Hub\houtai_pokemmo\Func\pic\jyh\data.png'
extracted_text = extract_text_from_image(image_path)
print("提取的文本:\n", extracted_text)
