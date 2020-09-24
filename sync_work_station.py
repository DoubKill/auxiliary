# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import datetime
import os
import time
import socket
import functools

import django
import logging

import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from system.models import SystemConfig, ChildSystemInfo
from work_station import models as md
from plan.models import ProductClassesPlan
from production import models as pd
from production import serializers as sz
from production.models import EquipStatus, TrainsFeedbacks, IfupReportWeightBackups, IfupReportBasisBackups, \
    IfupReportCurveBackups, IfupReportMixBackups, PlanStatus, ExpendMaterial
from work_station.models import IfupReportMix, IfupReportBasis

logger = logging.getLogger('sync_log')
# 该字典存储中间表与群控model及更新数据的映射关系


class MesUpClient(object):

    UP_TABLE_LIST = ["TrainsFeedbacks", "PalletFeedbacks", "EquipStatus", "PlanStatus", "ExpendMaterial"]
    Client = requests.request
    mes = ChildSystemInfo.objects.filter(system_name="MES").first()
    mes_ip = mes.link_address
    mes_status = mes.status
    API_DICT = {
        "TrainsFeedbacks" : "/api/v1/production/trains-feedbacks-batch/",
        "PalletFeedbacks" : "/api/v1/production/pallet-feedbacks-batch/",
        "EquipStatus": "/api/v1/production/equip-status-batch/",
        "PlanStatus": "/api/v1/production/plan-status-batch/",
        "ExpendMaterial": "/api/v1/production/expend-material-batch/"
    }


    @classmethod
    def sync(cls):
        if not cls.mes_ip or cls.mes_status != "联网":
            return
        sc_count = SystemConfig.objects.filter(config_name="sync_count").first().config_value
        for model_name in cls.UP_TABLE_LIST:
            temp = SystemConfig.objects.filter(config_name=model_name + "ID").first()
            temp_id = int(temp.config_value)
            model = getattr(pd, model_name)
            model_set = model.objects.filter(id__gte=temp_id)[:int(sc_count)]
            if model_set:
                new_temp_id = model_set[model_set.count()-1].id + 1
                Serializer = getattr(sz, model_name + "Serializer")
                serializer = Serializer(model_set, many=True)
                data = serializer.data
                datas = []
                for x in data:
                    if "equip_status" in x:
                        x.pop("equip_status")
                    if "stage" in x:
                        x.pop("stage")
                    datas.append(x)
                temp.config_value = new_temp_id
                ret = cls.Client("post", f"http://{cls.mes_ip}:8000{cls.API_DICT[model_name]}", json=datas)
                if ret.status_code <300:
                    temp.save()
                else:
                    logger.error(ret.text)

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
            s.bind((host, 60123))
        except:
            logger.info('already has an instance, this script will not be excuted')
            return
        return func(*args,**kwargs)
    return f


def update_plan_status(obj, status1, status2):
    """定时刷新计划状态"""
    if obj:
        equip_no = obj.equip_no
        product_no = obj.product_no
        plan_uid = obj.plan_classes_uid
        if "0" in equip_no:
            en = equip_no[-1]
        else:
            en = equip_no[1:3]
        model = getattr(md, "IfdownShengchanjihua" + en)
        if model.objects.filter(recstatus=status2, recipe=product_no, planid=plan_uid):
            PlanStatus.objects.filter(
                plan_classes_uid=plan_uid,
                product_no=product_no,
                equip_no=equip_no,
                status=status1
            ).update(status=status2)

def add_plan_status(obj, status):
    if obj:
        equip_no = obj.equip_no
        product_no = obj.product_no
        plan_uid = obj.plan_classes_uid
        if "0" in equip_no:
            en = equip_no[-1]
        else:
            en = equip_no[1:3]
        model = getattr(md, "IfdownShengchanjihua" + en)
        if model.objects.filter(recstatus=status, recipe=product_no, planid=plan_uid):
            instance = model.objects.filter(recstatus=status, recipe=product_no, planid=plan_uid).last()
            if not PlanStatus.objects.filter(plan_classes_uid=plan_uid, product_no=product_no,
                                         equip_no=equip_no, status=status,).exists():
                PlanStatus.objects.create(
                    plan_classes_uid=plan_uid,
                    product_no=product_no,
                    equip_no=equip_no,
                    status=status,
                    operation_user=instance.oper,
                    product_time=datetime.datetime.now(),
                )

def plan_status_monitor():
    """计划状态监听"""
    ps = PlanStatus.objects.filter(status="已下达").last()
    ps_stop = PlanStatus.objects.filter(status="待停止").last()
    ps_complete = PlanStatus.objects.filter(status="运行中").last()
    if ps:
        update_plan_status(ps, '已下达', '运行中')
    if ps_stop:
        update_plan_status(ps_stop, '待停止', '停止')
    if ps_complete:
        add_plan_status(ps_complete, '完成')



def main():
    # temp_list = dir(md)  # 原计划动态导入中间表，改为写死
    # 手动对中间表模型进行排序确保业务逻辑正确
    bath_no = 1 # 没有批次号编码,暂时写死
    temp_model_set = None
    temp = None
    current_trains = 0
    temp_list = ["IfupReportCurve", "IfupReportMix", "IfupReportWeight", "IfupMachineStatus", "IfupReportBasis"]
    for m in temp_list:
        temp_model = getattr(md, m)
        temp_model_set = temp_model.objects.filter(recstatus="待更新")
        if m == "IfupMachineStatus":
            """设备状态表"""
            # 每次循环最后检测，补充修改设备状态
            for temp in temp_model_set:
                if temp.运行状态 == 1:
                    equip_status = "运行中"
                elif temp.运行状态 == 2:
                    equip_status = "停机"
                elif temp.运行状态 == 3:
                    equip_status = "故障"
                else:
                    equip_status = "unknown"
                EquipStatus.objects.filter(plan_classes_uid=temp.计划号,
                                           equip_no=temp.机台号).update(status=equip_status)

        elif m == "IfupReportBasis":
            """车次报表主信息"""
            sync_data_list = []
            for temp in temp_model_set:
                uid = temp.计划号
                equip_no = str(temp.机台号)
                if len(equip_no) == 1:
                    equip_no = "Z0" + equip_no
                else:
                    equip_no = "Z" + equip_no
                product_no = temp.配方号  # 这里不确定是否一致
                # 暂时只能通过这个方案获取计划车次，理论上uid是唯一的
                pcp = ProductClassesPlan.objects.filter(
                    plan_classes_uid=uid
                ).last()
                begin_time_str = temp.开始时间
                end_time_str = temp.存盘时间
                if len(begin_time_str) == 15:
                    begin_time = datetime.datetime.strptime(begin_time_str, "%Y/%m/%d %H:%M")
                elif len(begin_time_str) ==19:
                    # begin_time = datetime.datetime.strptime(begin_time_str, "%Y/%m/%d %H:%M:%S")
                    begin_time = datetime.datetime.strptime(begin_time_str, "%Y-%m-%d %H:%M:%S")
                else:
                    continue
                if len(end_time_str) == 15:
                    end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M")
                elif len(end_time_str) ==19:
                    # end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M:%S")
                    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                else:
                    continue
                adapt_data_trains = {
                    "plan_classes_uid": uid,
                    "plan_trains": pcp.plan_trains if pcp else 0,
                    "actual_trains": temp.车次号,
                    "bath_no": bath_no,
                    "equip_no": equip_no,
                    "product_no": product_no,
                    "plan_weight": pcp.weight if pcp else 0,
                    "actual_weight": temp.总重量,
                    "begin_time": begin_time, # 2020/4/15 16:08
                    "end_time": end_time,
                    "operation_user": temp.员工代号,
                    "classes": pcp.work_schedule_plan.classes.global_name if pcp else "",
                    "product_time": end_time
                }
                sync_data_list.append(TrainsFeedbacks(**adapt_data_trains))
            TrainsFeedbacks.objects.bulk_create(sync_data_list)
            IfupReportBasisBackups.objects.bulk_create(list(temp_model_set))
        elif m == "IfupReportCurve":
            """车次报表工艺曲线数据表"""
            sync_data_list = []
            for temp in temp_model_set:
                uid = temp.计划号
                equip_no = str(temp.机台号)
                if len(equip_no) == 1:
                    equip_no = "Z0" + equip_no
                else:
                    equip_no = "Z" + equip_no
                end_time_str = temp.存盘时间
                if len(end_time_str) == 15:
                    end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M")
                elif len(end_time_str) == 19:
                    # end_time = datetime.datetime.strptime(end_time_str, "%Y/%m/%d %H:%M:%S")
                    end_time = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
                else:
                    continue
                mix_obj = IfupReportMix.objects.filter(计划号=uid, 配方号=temp.配方号, 机台号=temp.机台号)
                if mix_obj:
                    current_trains = mix_obj.last().密炼车次
                else:
                    current_trains = current_trains
                adapt_data = {
                    "plan_classes_uid": uid,
                    "equip_no": equip_no,  # 机台号可能需要根据规则格式化
                    "temperature": temp.温度,
                    "rpm": temp.转速,
                    "energy": temp.能量,
                    "power": temp.功率,
                    "pressure": temp.压力,
                    "current_trains": current_trains,
                    "status": "运行中",
                    "product_time": end_time,
                }
                sync_data_list.append(EquipStatus(**adapt_data))
            EquipStatus.objects.bulk_create(sync_data_list)
            IfupReportCurveBackups.objects.bulk_create(list(temp_model_set))
        elif m == "IfupReportMix":
            """车次报表步序表"""
            IfupReportMixBackups.objects.bulk_create(list(temp_model_set))
        elif m == "IfupReportWeight":
            """车次报表材料重量表"""
            sync_data_list = []
            for temp in temp_model_set:
                uid = temp.计划号
                product_no = temp.配方号
                equip_no = temp.机台号
                trains = temp.车次号
                plan_weight = temp.设定重量
                actual_weight = temp.实际重量
                material_no = temp.物料编码
                material_type = temp.物料类型
                if material_type == "C":
                    material_type = "炭黑"
                elif material_type == "O":
                    material_type = "油料"
                elif material_type == "P":
                    material_type = "胶料"
                material_name = temp.物料名称
                product_time = temp.存盘时间
                current_trains = trains
                adapt_data = {
                    "plan_classes_uid": uid,
                    "equip_no": equip_no,
                    "product_no": product_no,
                    "trains": trains,
                    "plan_weight": plan_weight,
                    "actual_weight": actual_weight,
                    "material_no": material_no,
                    "material_type": material_type,
                    "material_name": material_name,
                    "product_time": product_time
                }
                sync_data_list.append(ExpendMaterial(**adapt_data))
            ExpendMaterial.objects.bulk_create(sync_data_list)
            IfupReportWeightBackups.objects.bulk_create(list(temp_model_set))
        else:
            # 该分支正常情况执行，若执行需告警
            logger.error("出现未知同步表，请立即检查")
        temp_model_set.update(recstatus="更新完成")
    # 改部分代码目前未生效
    if temp is IfupReportBasis:
        plan_no = temp.计划号
        product_no = temp.配方号
        equip_str = str(temp.机台号)
        if len(equip_str) == 1:
            equip_no = "Z0" + equip_str
        else:
            equip_no = "Z" + equip_str
        product_time = temp.存盘时间
        actual_trains = temp.车次号
        current_trains = actual_trains
        plan_trains = pcp.plan_trains if pcp else 0
        model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix',
                      # 'IfdownRecipePloy', 'IfdownRecipeOil1','IfdownRecipeCb',
                      'IfdownPmtRecipe', "IfdownRecipeWeigh"]
        if actual_trains < plan_trains:
            status = "运行中"
            model_name = getattr(md, model_list[0] + equip_str)
            instance = model_name.objects.all().first()
            if instance:
                if instance.recstatus == "停止":
                    status = "停止"
        # elif: 这里预留一个分支判断，当满足时可能计划被删除
        else:
            status = "已完成"
            for model_str in model_list:
                model_name = getattr(md, model_str + equip_str)
                model_name.objects.all().update(recstatus='完成')
        operation_user = temp.员工代号
        if not operation_user:
            operation_user = ""
        PlanStatus.objects.create(plan_classes_uid=plan_no,
                                       product_no=product_no,
                                       equip_no=equip_no,
                                       operation_user=operation_user,
                                       product_time=product_time,
                                       status=status
                                       )


@one_instance
def run():
    global current_trains
    while True:
        try:
            main()
            plan_status_monitor()
            MesUpClient.sync()
        except Exception as e:
            logger.error(e)
        time.sleep(5)

if __name__ == "__main__":
    # 问题1 recstatus字段是否要修改 文档1中是字符，sql建的表是整型
    # 2 两张上行表中的设备数据取拿张，或者说策略
    # 什么时候写入车次反馈数据什么时候回写入批次反馈数据，跟万隆对接只有车次数据
    # ifup上行中间表是在每车完成同步插入数据的吗, 理论上来说对于万隆应该是个双写的逻辑
    run()
    # 后续进程函数或者类封装


    #TODO
    # 1. 该脚本不在是一个单独的上行脚本，若报产数据上来没有计划，则需在计划表里新增一条数据
    # 2. 预留入口，可以扩展其他功能