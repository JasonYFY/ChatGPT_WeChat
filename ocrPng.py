# from io import BytesIO

# from PIL import Image
# import pytesseract
# import cv2
# import numpy as np
# from matplotlib import pyplot as plt
# import easyocr
# from wand.image import Image as WandImage
# from wand.drawing import Drawing
# from wand.color import Color
import logging
from paddleocr import PaddleOCR
# 移除所有通过其他模块或库添加的处理器（因为导入这个模块会有多的，打印两次日志，所以需要移除）
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# def recognize_text(image_bytes):
#     image = Image.open(BytesIO(image_bytes))
#     # image = image_border(image)
#     # plt.imshow(image)
#     # plt.show()
#     # 对图片进行放大，这里设定为原来的2倍大小
#     img_resized = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
#     #     # 保存放大后的图片
#     img_resized.save('bigPic.jpg')
#
#     # 使用Tesseract进行文字识别
#     text = pytesseract.image_to_string(img_resized,lang='chi_sim')
#
#     return text

def recognize_text_Paddle(image_bytes):
    # image = Image.open(BytesIO(image_bytes))
    # image = image_border(image)
    # plt.imshow(image)
    # plt.show()

    ocr = PaddleOCR(use_angle_cls=False, lang="ch")  # need to run only once to download and load model into memory
    result = ocr.ocr(image_bytes, cls=False)

    txt = ""  # 检测识别结果
    for line in result[0]:
        # print(line[1][0])
        txt += line[1][0] + "\n"  # 取出文本
    return txt


# image = Image.open('C:\\Users\\yifangyu\\Desktop\\screensh1.png')
# text = pytesseract.image_to_string(image,lang='chi_sim')
# print(text)

# reader = easyocr.Reader(['ch_sim', 'en'], gpu=False) # 只需要运行一次就可以将模型加载到内存中
# def recognize_text_easyocr(image_bytes):
#     # plt.imshow(image)
#     # plt.show()
#     result = reader.readtext(image_bytes)
#     # print(result)
#     for i in result:
#         word = i[1]
#         # print(word)
#         return word
#     return ''

# 读取图片字节数据（替换成你自己的图片字节数据）
# with open('/home/yifangyujason/ChatGPT_WeChat/tipPic_1.png', 'rb') as image_file:
#     image_bytes = image_file.read()
# # # # # 调用文字识别函数
# result_text = recognize_text_Paddle(image_bytes)
# result_text = recognize_text_easyocr(image_bytes)
# # #
# # # # 打印识别结果
# print(result_text)

