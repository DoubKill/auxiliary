# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/25
name: 
"""
import functools
import json
import os
import socket

import django
import logging

import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()


from system.models import SystemConfig, ChildSystemInfo, AsyncUpdateContent


logger = logging.getLogger(__name__)


def one_instance(func):
    '''
    如果已经有实例在跑则退出
    '''
    @functools.wraps(func)
    def f(*args,**kwargs):
        try:
        # 全局属性，否则变量会在方法退出后被销毁
            global s
            s = socket.socket()
            host = socket.gethostname()
            s.bind((host, 60124))
        except:
            print('already has an instance, this script will not be excuted')
            return
        return func(*args,**kwargs)
    return f


class SystemSync(object):


    # 设置单例模式
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_inst'):
            cls._inst = super(SystemSync, cls).__new__(cls, *args, **kwargs)
        return cls._inst

    def __init__(self):
        self.sync_data_list = []

    # 获取当前系统状态
    @property
    @classmethod
    def if_system_online(cls):
        config_value = SystemConfig.objects.filter(config_name="system_name").first().config_value
        child_system = ChildSystemInfo.objects.filter(system_name=config_value).first()
        if child_system:
            child_system_status = child_system.status
            if child_system_status == "联网":
                return True
            return False
        return False

    # 进行同步
    def sync(self):
        if self.if_system_online:
            sync_set = AsyncUpdateContent.objects.filter(recv_flag=False)
            for instance in sync_set:
                id = instance.id,
                model_name = instance.src_table_name,
                body_data = instance.content,
                address = instance.dst_address,
                method = instance.method
                requests.request(method, address, json=json.loads(body_data))

        logger.warning("系统未联网，同步未执行")


    def sync_feedback(self):
        pass


@one_instance
def run():
    while True:
        print()
    pass

if __name__ == '__main__':
    run()