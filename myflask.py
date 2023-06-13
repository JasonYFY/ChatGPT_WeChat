# -*- coding: utf-8 -*-
# 导入模块
import hashlib
import time

import yaml
from flask import Flask, request, make_response
from flask import abort
from wechatpy import parse_message, create_reply, WeChatClient
from wechatpy.replies import VoiceReply

from common.log import logger
# 导入自定义类
from getAccessToken import Auth0
from gptManage import gptMessageManage
from whiteIPManage import whiteIP

##############################读取配置##########################
with open('config/config.yml', 'r') as f:
    configs = yaml.load(f, Loader=yaml.FullLoader)
##############################设置微信相关参数##########################
appid = configs['wechat']['appid']
secret = configs['wechat']['secret']
if configs['wechat']['ip_detection'] or configs['azure']['trans_to_voice']:
    client = WeChatClient(appid, secret)
else: 
    client = ''
wechattoken = configs['wechat']['token']

##############################设置IP白名单,预防doss##########################
mywhiteIP = whiteIP(client)

##############################openai基础设置##########################
msgsmanag = gptMessageManage(client,configs)


app = Flask(__name__)
app.debug = True

# @app.route("/")
# def hello():
#     return "Hello test!"

@app.route('/wechat/', methods=['GET', 'POST']) 
def wechat():
    global reply
    global msgsmanag
    global wechattoken
    global mywhiteIP
    if configs['wechat']['ip_detection']:
        if not mywhiteIP.is_white_ip(request.remote_addr):
            abort(404)
    if request.method == 'GET':
        token = wechattoken# 设置 wechat token
        data = request.args
        signature = data.get('signature', '')
        timestamp = data.get('timestamp', '')
        nonce = data.get('nonce', '')
        echostr = data.get('echostr', '')
        s = sorted([timestamp, nonce, token])
        s = ''.join(s)
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            response = make_response(echostr)
            return response
    else:
        msg = parse_message(request.get_data())
        if msg.type == 'text':
            cctime = int(time.time())
            # 内置英语对话模板
            if msg.content[:4]=='英语对话':
                tt = f'''Now please be my English teacher. We will simulate an English chat, and in addition to answering, you also need to point out my expression errors. Today's topic is "{msg.content.split(' ')[1]}". Your chat response needs to guide me to complete the English topic. If you understand, please reply with the requirements for today's chat practice.'''
                rtext = msgsmanag.get_response(msg,cctime,tt)
            else:
                rtext = msgsmanag.get_response(msg,cctime,msg.content)
            rt = str(rtext).strip()
            reply = create_reply(rt, message=msg)#创建消息
            return reply.render()
        if msg.type == 'voice':
            cctime = int(time.time())
            try:
                rtext = msgsmanag.get_response(msg,cctime,msg.recognition)
            except Exception as e:
                rtext = '您发送了一条语音消息！'
            # print('打印返回的内容',rtext)
            if isinstance(rtext, list):
                # print('返回的是列表',rtext)
                reply = VoiceReply(message=msg)
                reply.media_id = rtext[0]
            else:
                reply = create_reply(rtext, message=msg)
            # 等候1.2s的原因是，素材上传至微信后台需要时间审核, 否则回复的语音会存在问题
            time.sleep(1.2)
            # 需要判断一下等候1.2S之后，是否有微信的二次请求
            if cctime == msgsmanag.msgs_time_dict.get(str(msg.id),''):
                return reply.render()
        if msg.type == 'image':
            rtext = '您发送了一张图片！'
            reply = create_reply(rtext, message=msg)#创建消息
            return reply.render()#回复消息
        return ''

@app.route('/getAccessToken/', methods=['POST'])
def getAccessToken():
    req = request.get_json()  # 获取JSON数据
    username = req.get('username')  # 获取参数username
    password = req.get('password')  # 获取参数password
    try:
        access_token = Auth0(username, password).auth(True)
        logger.info('获取的accessToken：%s', access_token)
        return {'status': 'success', 'data': access_token}
    except Exception as e:
        message = str(e)
        logger.error('getAccessToken接口报错：%s', e)
    return {'status': 'fail', 'message': message}

@app.route('/refreshToken/', methods=['POST'])
def refreshToken():
    req = request.get_json()  # 获取JSON数据
    refreshToken = req.get('refresh_token')  # 获取参数refresh_token
    try:
        access_token = Auth0.refresh(refreshToken)
        logger.info('刷新的accessToken：%s', access_token)
        return {'status': 'success', 'data': access_token}
    except Exception as e:
        message = str(e)
        logger.error('refreshToken接口报错：%s', e)
    return {'status': 'fail', 'message': message}

if __name__ == '__main__':
    app.run( host = '0.0.0.0')
