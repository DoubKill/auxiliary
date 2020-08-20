# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from django.db.models.base import ModelBase
from work_station import models as md

def run():
    temp_list = dir(md)
    temp_list.sort(key=lambda x: x[-1])

    for m in temp_list:
        temp_model = getattr(md, m)
        if isinstance(temp_model, ModelBase) and m.startswith("Ifup"):
            print(m)




if __name__ == "__main__":
    run()