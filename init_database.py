# coding: utf-8
"""项目初始化脚本"""

import os

import django
import shutil

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from system.models import User
from recipe.models import BaseAction, BaseCondition


def add_condition_action():
    action_add = {
        "加炭黑": 2,
        "加胶料": 1,
        "加油1": 4,
        "开卸料门": 256,
        "关卸料门": 512,
        "升上顶栓": 1024,
        "加油2": 8,
        "降上顶栓": 2048,
        "上顶栓清扫": 4096,
        "保持": 16384,
        "开加料门": 64,
        "关加料门": 128,
        "加小料": 16,
        "上顶栓浮动": 8192,
        "升上顶栓开卸料门": 1280,
        "加炭黑油1": 6,
        "加炭黑油2": 10,
        "加炭黑油1油2": 14,
        "加油1油2": 12,
        "升上顶栓关卸料门": 1536,
        "降上顶栓开卸料门": 2304
    }

    cond_add = {
        "时间": 1,
        "温度": 2,
        "能量": 4,
        "时间与温度": 8,
        "时间与能量": 16,
        "温度与能量": 32,
        "时间或能量": 5,
        "能量或温度": 6,
        "时间或温度": 3,
        "同步执行": 0
    }

    for key, value in action_add.items():
        BaseAction.objects.get_or_create(
            action=key,
            code=value
        )
    # 添加状态信息
    for key, value in cond_add.items():
        BaseCondition.objects.get_or_create(
            condition=key,
            code=value
        )


def main():
    print('开始迁移数据库')
    apps = ('system', 'basics', 'plan', 'production', 'recipe', 'work_station')

    for app in apps:
        try:
            shutil.rmtree("{}/migrations".format(app))
        except Exception:
            pass

    os.system(
        'python manage.py makemigrations {}'.format(
            ' '.join(apps)
        ))
    os.system('python manage.py migrate')

    print('创建超级管理员...')
    User.objects.create_superuser('mes', '123456@qq.com', '123456')
    add_condition_action()


if __name__ == '__main__':
    main()
