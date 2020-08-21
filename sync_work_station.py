# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import datetime
import os
import time

import django
import logging


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from django.db.models.base import ModelBase
from work_station import models as md
from plan.models import ProductClassesPlan
from production.models import EquipStatus, TrainsFeedbacks
from work_station.models import IfupReportMix

logger = logging.getLogger(__name__)
# 该字典存储中间表与群控model及更新数据的映射关系
sync_model_map = {
    "IfupMachineStatus": EquipStatus,
    "IfupReportBasis": (),
    "IfupReportCurve": (),
    "IfupReportMix": (),
    "IfupReportWeight": (),
}
field_map = {

    "IfupMachineStatus": {
        "计划号": "plan_classes_uid",
        "配方号": "",
        "运行状态": "status",
        "机台号": "equip_no",
    },

    "IfupReportBasis": {
        "车次号": "",
        "开始时间": "start_time",  # 格式 2020/4/15 16:08,
        "消耗时间": "",
        "间隔时间": "",
        "排胶温度": "temperature",
        "排胶功率": "power",
        "排胶能量": "energy",
        "作业方式": "",
        "控制方式": "",
        "员工代号": "operation_user",
        "总重量": "",
        "胶料重量": "actual_weight",
        "炭黑重量": "",
        "油1重量": "",
        "油2重量": "",
        "加胶时间": "",
        "加炭黑时间": "",
        "加油1时间": "",
        "加油2时间": "",
    },

    "IfupReportCurve": {
        "温度": "temperature",
        "能量": "energy",
        "功率": "power",
        "压力": "pressure",
        "转速": "rpm",
    },

    "IfupReportMix": {
        "步骤号": "",
        "条件": "",
        "时间": "",
        "温度": "temperature",
        "能量": "energy",
        "功率": "power",
        "压力": "pressure",
        "转速": "rpm",
        "动作": "",
        "密炼车次": "",
        "计划号": "plan_classes_uid",
        "配方号": "",
        "机台号": "equip_no",
    },

    "IfupReportWeight": {
        "车次号": "",
        "物料名称": "",
        "设定重量": "",
        "实际重量": "",
        "秤状态": "",
        "计划号": "plan_classes_uid",
        "配方号": "",
        "机台号": "equip_no",
        "物料编码": "",
        "物料类型": "",
        "存盘时间": "",

    }

}


def main():
    # temp_list = dir(md)  # 原计划动态导入中间表，改为写死
    # 手动对中间表模型进行排序确保业务逻辑正确
    bath_no = 1 # 没有批次号编码,暂时写死
    temp_list = ["IfupReportCurve", "IfupReportBasis", "IfupReportMix", "IfupReportWeight", "IfupMachineStatus"]
    for m in temp_list:
        temp_model = getattr(md, m)
        if isinstance(temp_model, ModelBase) and m.startswith("Ifup"):
            try:
                temp_model_set = temp_model.objects.filter(recstatus="等待")
                temp_model_set.update(recstatus="运行中")
                if m == "IfupMachineStatus":
                    for temp in temp_model_set:
                        EquipStatus.objects.filter(plan_classes_uid=temp.get("计划号"),
                                                   equip_no=temp.get("机台号")).update(status=temp.get("运行状态"))
                elif m == "IfupReportBasis":
                    sync_data_list = []
                    for temp in temp_model_set:
                        uid = temp.get("计划号")
                        equip_no = temp.get("机台号")
                        product_no = temp.get("配方号")  # 这里不确定是否一致
                        # 暂时只能通过这个方案获取计划车次，理论上uid是唯一的
                        pcp = ProductClassesPlan.objects.filter(plan_classes_uid=uid, equip_no=equip_no).first()
                        begin_time_str = temp.get("开始时间")
                        end_time_str = temp.get("存盘时间")
                        if len(begin_time_str) == 15:
                            begin_time = datetime.datetime.strptime(begin_time_str, "%Y/%m/%d %H:%M")
                        elif len(begin_time_str) ==18:
                            begin_time = datetime.datetime.strptime(begin_time_str, "%Y/%m/%d %H:%M:%S")
                        else:
                            continue
                        if len(end_time_str) == 15:
                            end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M")
                        elif len(end_time_str) ==18:
                            end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M:%S")
                        else:
                            continue
                        adapt_data_trains = {
                            "plan_classes_uid": uid,
                            "plan_trains": pcp.plan_trains,
                            "actual_trains": temp.get("车次号"),
                            "bath_no": bath_no,
                            "equip_no": equip_no,
                            "product_no": product_no,
                            "plan_weight": pcp.weight,
                            "actual_weight": temp.get("总重量"),
                            "begin_time": begin_time, # 2020/4/15 16:08
                            "end_time": end_time,
                            "operation_user": temp.get("员工代号"),
                            "classes": pcp.classes_detail.classes.global_name,
                        }
                        sync_data_list.append(**adapt_data_trains)
                    TrainsFeedbacks.objects.bulk_create(sync_data_list)
                elif m == "IfupReportCurve":
                    sync_data_list = []
                    for temp in temp_model_set:
                        uid = temp.get("计划号")
                        current_trains = IfupReportMix.objects.filter(计划号=uid, 配方号=temp.get("配方号"),
                                                                      机台号=temp.get("机台号")).first().密炼车次
                        adapt_data = {
                            "plan_classes_uid": uid,
                            "equip_no": temp.get("机台号"),  # 机台号可能需要根据规则格式化
                            "temperature": temp.get("温度"),
                            "rpm": temp.get("转速"),
                            "energy": temp.get("能量"),
                            "power": temp.get("功率"),
                            "pressure": temp.get("压力"),
                            "current_trains": current_trains,
                        }
                        sync_data_list.append(EquipStatus(**adapt_data))
                    EquipStatus.objects.bulk_create(sync_data_list)
                elif m == "IfupReportMix":
                    pass
                elif m == "IfupReportWeight":
                    #TODO
                    # 暂时不熟悉原材料管理8.22补充
                    pass
                else:
                    # 该分支正常情况执行，若执行需告警
                    print("出现未知同步表，请立即检查")
                    pass
                temp_model_set.update(recstatus="上传完成")
            except Exception as e:
                logger.error(f"同步过程出现异常，参考异常:{e}，请及时修正")
            else:
                temp_model_set.update(recstatus="完成")
                time.sleep(5)
            # 适配器模式作废，直接if elif搞
            # 获取映射model
            # 生成model对应data
            # 进行更新
            # temp_plan_no_list = temp_model.objects.filter(recstatus=2)
            # temp_set = temp_model.objects.filter(recstatus="按照涉及改为中文的话这部分状态对应的字段需要改为字符类型")
            # 获取映射model
            # sync_model = sync_model_map.get(m)
            # sync_data = {}
            # sync_model, data = mid_model_map.get(m)
            # sync_model.objects.create(**data)

def run():
    while True:
        main()


if __name__ == "__main__":
    # 问题1 recstatus字段是否要修改 文档1中是字符，sql建的表是整型
    # 2 两张上行表中的设备数据取拿张，或者说策略
    # 什么时候写入车次反馈数据什么时候回写入批次反馈数据
    # ifup上行中间表是在没车完成同步插入数据的吗
    run()