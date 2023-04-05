**简介：**

未认证微信公众号接入chatgpt，基于Flask，实现个人微信公众号【无认证】接入ChatGPT【GPT-3.5-Turbo】

**背景：**

最近看到ChatGPT提供了API接口，手上刚好有台服务器和一个公众号，所以想着写一个聊天机器人🤖玩一玩。不过只有一个没有认证的个人公众号(资源有限😭)，这个公众号的限制就是：

1.只能被动回复用户消息，用户发送一条消息到公众号，服务器只能针对这个请求回复一条消息，不能再额外回复消息(客服消息)；

2.每次必须在15s以内回复消息，公众号平台在发送请求到服务器后，如果5s内没收到回复，会再次发送请求等候5秒，如果还是没有收到请求，最后还会发送一次请求，所以服务器必须在15s以内完整消息的处理。

具体处理方式查看代码。新手项目，有不足之处还请包含并欢迎指正，谢谢~

**需求：**

一台服务器（需要能访问openai接口的，可能需要海外的~）

python(3.8)主要模块：flask, wechatpy

**演示：**

公众号：Tory的实验室，关注发送消息即可体验。

![image-20230305121520474](https://github.com/ToryPan/ChatGPT_WeChat/blob/main/pic/image-20230305121520474.png)

**使用方法：**

设置myflask.py里面的参数：

```python
##############################openai基础设置##########################
tokens = ['Bearer sk-XXX1','Bearer sk-XXX2']
max_tokens = 250
model = 'gpt-3.5-turbo'
temperature = 0.8
rsize = 200 # 设置每条消息的回复长度，超过长度将被分割
##############################wechat基础设置##########################
wechattoken = 'wechattoken'
```

启动flask

```sh
export FLASK_APP=myflask

flask run --host=0.0.0.0 --port=80
# 或者
nohup flask run --host=0.0.0.0 --port=80 >> /home/jupyter/flask/log/wechat.log 2>&1 &
```


