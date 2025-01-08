import yaml
from apscheduler.schedulers.background import BackgroundScheduler
# 创建一个后台调度器
from signIn import signIn
from commonUtils.log import logger



def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class timerTask:

    def __init__(self):
        ##############################读取配置##########################
        with open('config/config.yml', 'r', encoding='utf-8') as f:
            configs = yaml.load(f, Loader=yaml.FullLoader)
        username = configs['signIn']['username']
        password = configs['signIn']['password']


        scheduler = BackgroundScheduler()
        # 添加定时任务
        scheduler.add_job(signIn.singInOfHuaxiashuyu, 'cron', day_of_week='*', hour=7, minute=0,args=(username, password),max_instances=3)

        # 设置每隔6个小时触发一次任务
        #scheduler.add_job(NewBing.checkCF, 'interval', hours=5,args=(auth,usernameCF, passwordCF))
        # scheduler.add_job(NewBing.checkCF, 'cron', day_of_week='*', hour=7, minute=1,args=(auth,usernameCF, passwordCF))

        # 启动调度器
        scheduler.start()
        logger.info('定时任务启动成功')

