import yaml
from cachetools import TTLCache
from commonUtils.log import logger
import google.generativeai as genai





class geminiAi:
    # 创建一个最多包含3个元素的自动过期的哈希映射，每个元素的生存时间为24小时
    cache = TTLCache(maxsize=30, ttl=60 * 60 * 24)
    with open('config/config.yml', 'r', encoding='utf-8') as f:
        configs = yaml.load(f, Loader=yaml.FullLoader)
    imagePath = configs['bardAi']['image_path']
    apiKey = configs['bardAi']['api_key']

    genai.configure(api_key=apiKey)
    model = genai.GenerativeModel('gemini-1.0-pro-latest')


    @staticmethod
    def getAnswer(content: str, conversationId: str, imageFileName: str):
        # logger.info('询问的内容：{}'.format(content))
        gemini = geminiAi.cache.get(conversationId)
        # logger.info('获取的bard：{}'.format(bard))
        if gemini is None:
            logger.info('获取新的gemini，新的conversationId：{}'.format(conversationId))
            gemini = geminiAi.model.start_chat(history=[])
        geminiAi.cache[conversationId] = gemini

        if imageFileName:
            image_path = geminiAi.imagePath + imageFileName
            logger.info('读取图片路径：{}'.format(image_path))
            image = open(image_path, 'rb').read()  # (jpeg, png, webp) are supported.
            res = gemini.generate_content([content,image])
        else:
            res = gemini.send_message(content)

        resContent = res.text
        return resContent, None




