# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import os
import django

from production.models import EquipStatus

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from django.db.models.base import ModelBase
from work_station import models as md

# 该字典存储中间表与群控model及更新数据的映射关系
sync_model_map =   {
    "IfupMachineStatus": EquipStatus,
    "IfupReportBasis": (),
    "IfupReportCurve": (),
    "IfupReportMix": (),
    "IfupReportWeight": (),
}
field_map = {

}
def run():
    temp_list = dir(md)
    for m in temp_list:
        temp_model = getattr(md, m)
        if isinstance(temp_model, ModelBase) and m.startswith("Ifup"):
            # temp_plan_no_list = temp_model.objects.filter(recstatus=2)
            temp_set = temp_model.objects.filter(recstatus="按照涉及改为中文的话这部分状态对应的字段需要改为字符类型")
            # 获取映射model
            sync_model = sync_model_map.get(m)
            sync_data = {}

            # 获取映射model
            # 生成model对应data
            # 进行更新
            # sync_model, data = mid_model_map.get(m)
            # sync_model.objects.create(**data)








if __name__ == "__main__":
    run()