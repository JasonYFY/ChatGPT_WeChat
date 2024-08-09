#from matplotlib import pyplot as plt
import cv2
import numpy as np


def _tran_canny(image):
    """消除噪声"""
    image = cv2.GaussianBlur(image, (3, 3), 0)
    return cv2.Canny(image, 50, 150)

def detect_displacement(img_slider_path, image_background_path):
    """detect displacement"""

    # 将字节数据转换为NumPy数组
    image_slider = np.frombuffer(img_slider_path, dtype=np.uint8)
    image_background = np.frombuffer(image_background_path, dtype=np.uint8)

    # 通过cv2.imdecode()将NumPy数组解码为图像
    image = cv2.imdecode(image_slider, flags=cv2.IMREAD_COLOR)
    template = cv2.imdecode(image_background, flags=cv2.IMREAD_COLOR)

    # 检查是否成功读取图像
    if image is None:
        raise Exception("无法从base64编码字符串读取图像")

    # # 参数0是灰度模式
    # image = cv2.imread(img_slider_path, 0)
    # template = cv2.imread(image_background_path, 0)

    # 寻找最佳匹配
    res = cv2.matchTemplate(_tran_canny(image), _tran_canny(template), cv2.TM_CCOEFF_NORMED)
    # 最小值，最大值，并得到最小值, 最大值的索引
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    top_left = max_loc[0]  # 横坐标
    # 展示圈出来的区域
    # x, y = max_loc  # 获取x,y位置坐标

    # w, h = image.shape[::-1]  # 宽高
    # cv2.rectangle(template, (x, y), (x + w, y + h), (7, 249, 151), 2)
    # show(template)
    # plt.imshow(template)
    # plt.show()
    return top_left
