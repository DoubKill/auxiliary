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

from django.db.transaction import atomic
from recipe.models import Material
from system.models import SystemConfig, ChildSystemInfo
from mes.conf import MES_PORT
from work_station.models import I_ORDER_STATE_V, BatchReport, MaterialsConsumption
from plan.models import ProductClassesPlan
from production import models as pd
from production import serializers as sz
from production.models import EquipStatus, TrainsFeedbacks, IfupReportWeightBackups, IfupReportBasisBackups, \
    IfupReportCurveBackups, IfupReportMixBackups, PlanStatus, ExpendMaterial

logger = logging.getLogger('sync_log')
# 该字典存储中间表与群控model及更新数据的映射关系


class MesUpClient(object):
    # 生产数据上报mes
    UP_TABLE_LIST = [
        "TrainsFeedbacks", "PalletFeedbacks", "EquipStatus", "PlanStatus", "ExpendMaterial",
        "ProcessFeedback", "AlarmLog"]
    Client = requests.request
    mes = ChildSystemInfo.objects.filter(system_name="MES").first()
    mes_ip = mes.link_address
    mes_status = mes.status
    API_DICT = {
        "TrainsFeedbacks" : "/api/v1/production/trains-feedbacks-batch/",
        "PalletFeedbacks" : "/api/v1/production/pallet-feedbacks-batch/",
        "EquipStatus": "/api/v1/production/equip-status-batch/",
        "PlanStatus": "/api/v1/production/plan-status-batch/",
        "ExpendMaterial": "/api/v1/production/expend-material-batch/",
        "ProcessFeedback": "/api/v1/production/process-feedback-batch/",
        "AlarmLog": "/api/v1/production/alarm-log-batch/",
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
                if model_name in ["TrainsFeedbacks", "PalletFeedbacks"]:
                    Serializer = getattr(sz, model_name + "UpSerializer")
                else:
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
                ret = cls.Client("post", f"http://{cls.mes_ip}:{MES_PORT}{cls.API_DICT[model_name]}", json=datas)
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



def add_Z04_plan_status():
    order_set_status = I_ORDER_STATE_V.objects.using("H-Z04").filter(order_start_date__gte=(datetime.datetime.now() -
                                                                     datetime.timedelta(days=1)),
                                                                     order_status__in=["FINISHED", "UNFINISHED"])
    for order in order_set_status:
        pcp_set = ProductClassesPlan.objects.filter(plan_classes_uid=order.order_name)
        if not pcp_set.exists():
            continue
        if PlanStatus.objects.filter(plan_classes_uid=order.order_name,
                                         product_no=order.recipe_name,
                                         equip_no=order.line_name,
                                         status__in=["完成", "停止"]).exists():
            continue

        if order.order_status == "FINISHED":
            status = "完成"
        elif order.order_status == "UNFINISHED":
            status = "停止"
        else:
            status = "unknown"

        PlanStatus.objects.create(
            plan_classes_uid=order.order_name,
            product_no=order.recipe_name,
            equip_no=order.line_name,
            status=status,
            operation_user="hf",
            product_time=datetime.datetime.now()
        )
        pcp_set.update(status=status, plan_trains=order.batches_set)


def update_Z04_plan_status():
    run_status = "运行中"
    plan_set = PlanStatus.objects.filter(equip_no="Z04", status="已下达", product_time__isnull=True)
    for plan in plan_set:
        if I_ORDER_STATE_V.objects.using("H-Z04").filter(order_name=plan.plan_classes_uid, recipe=plan.product_no,
                                                      line_name="Z04", order_status="PRODUCTION").exists():
            plan.status = run_status
            plan.save()
            try:
                ProductClassesPlan.objects.filter(plan_classes_uid=plan.plan_classes_uid).update(status=run_status)
            except Exception as e:
                logger.error(e)




def plan_status_monitor():
    """计划状态监听"""
    add_Z04_plan_status()
    update_Z04_plan_status()


#Z04 数据需单独上传
@atomic()
def hf_trains_up():
    tf = TrainsFeedbacks.objects.filter(equip_no="Z04").order_by("product_time").last()
    if tf:
        batch_set = BatchReport.objects.using("H-Z04").filter(batr_end_date__gt=tf.product_time).values("batr_batch_quantity_set", "batr_batch_number",
                  "batr_recipe_code", "batr_recipe_version", "batr_order_number", "batr_user_name",
                  "batr_batch_weight", "batr_start_date", "batr_end_date", "batr_quality", "batr_total_spec_energy", "batr_tot_integr_energy",
                  "batr_total_revolutions", "batr_cycle_time", "batr_mixing_time", "batr_drop_cycle_time", "batr_transition_temperature")
    else:
        batch_set = BatchReport.objects.using("H-Z04").filter().values("batr_batch_quantity_set",
                                                                                            "batr_batch_number",
                                                                                            "batr_recipe_code",
                                                                                            "batr_order_number",
                                                                                            "batr_recipe_version",
                                                                                            "batr_batch_weight",
                                                                                            "batr_start_date",
                                                                                            "batr_end_date",
                                                                                            "batr_quality",
                                                                                            "batr_total_spec_energy",
                                                                                            "batr_tot_integr_energy",
                                                                                            "batr_total_revolutions",
                                                                                            "batr_cycle_time",
                                                                                            "batr_mixing_time",
                                                                                            "batr_drop_cycle_time",
                                                                                            "batr_transition_temperature",
                                                                                            "batr_user_name")
    temp1 = None
    for temp in batch_set:
        pcp_set = ProductClassesPlan.objects.filter(plan_classes_uid=temp.get("batr_order_number"))
        if not pcp_set.exists():
            continue
        if TrainsFeedbacks.objects.filter(plan_classes_uid=temp.get("batr_order_number"), actual_trains=temp.get('batr_batch_number')):
            continue
        plan = pcp_set.last()
        try:
            plan_weight = plan.weight if plan.weight else 23000
            class_name = plan.work_schedule_plan.classes.global_name
            if temp1:
                interval_time = (temp.get("batr_start_date") - temp1.get("batr_end_date")).total_seconds()
            else:
                interval_time = 15
            consume_time = (temp.get("batr_end_date") - temp.get("batr_start_date")).total_seconds()
            train = dict(
                plan_classes_uid = temp.get("batr_order_number"),
                plan_trains =temp.get("batr_batch_quantity_set"),
                actual_trains = temp.get("batr_batch_number"),
                bath_no = 1,
                equip_no = "Z04",
                product_no = temp.get("batr_recipe_code"),
                plan_weight=plan_weight,
                actual_weight = temp.get("batr_batch_weight", 230)*100,
                begin_time = temp.get("batr_start_date"),
                end_time = temp.get("batr_end_date"),
                operation_user = temp.get("batr_user_name"),
                classes = class_name,
                product_time = temp.get("batr_end_date"),
                control_mode="远控",
                operating_type = "自动",
                evacuation_time = int(temp.get("batr_drop_cycle_time")),
                evacuation_temperature = temp.get("batr_transition_temperature"),
                evacuation_energy = int(temp.get("batr_tot_integr_energy")),
                interval_time=int(interval_time),
                mixer_time=int(temp.get("batr_mixing_time")),
                consum_time=int(consume_time),
            )
            temp1 = temp
            TrainsFeedbacks.objects.create(**train)
        except Exception as e:
            print(e)
            logger.error(f"Z04车次报表上行失败:{e}")
            continue


@atomic()
def consume_data_up():
    ep = ExpendMaterial.objects.filter(equip_no="Z04").order_by("product_time").last()
    if ep:
        consume_set = MaterialsConsumption.objects.using("H-Z04").filter(maco_end_date__gt=ep.product_time).values(
            "maco_date", "maco_order_number", "maco_mat_code", "maco_consumed_quantity", "maco_end_date", "maco_recipe_code",
            "insert_user", "maco_set_quantity", "maco_batch_number")
    else:
        consume_set = MaterialsConsumption.objects.using("H-Z04").filter().values(
            "maco_date", "maco_order_number", "maco_mat_code", "maco_consumed_quantity", "maco_end_date",
            "maco_recipe_code", "insert_user", "maco_set_quantity", "maco_batch_number"
        )
    for temp in consume_set:
        if not ProductClassesPlan.objects.filter(plan_classes_uid=temp.get("maco_order_number")).exists():
            continue
        if ExpendMaterial.objects.filter(plan_classes_uid=temp.get("maco_order_number"), trains=temp.get('maco_batch_number'),
                                         material_no=temp.get("maco_mat_code")):
            continue
        try:
            material_name = temp.get("maco_mat_code")
            if not material_name:
                continue
            material = Material.objects.filter(material_name=material_name).last()
            if material:
                material_no = material.material_no
                material_type = material.material_type.global_name
            else:
                continue
            consume = dict(
                plan_classes_uid=temp.get("maco_order_number"),
                equip_no ="Z04",
                product_no =temp.get("maco_recipe_code"),
                trains =temp.get("maco_batch_number"),
                plan_weight =temp.get("maco_set_quantity") * 100,
                actual_weight =temp.get("maco_consumed_quantity") * 100,
                material_no =material_no,
                material_type=material_type,
                material_name=temp.get("maco_mat_code"),
                product_time=temp.get("maco_end_date"),
            )
            ExpendMaterial.objects.create(**consume)
        except Exception as e:
            print(e)
            logger.error(f"Z04消耗报表上行失败:{e}")
            continue



@one_instance
def run():
    while True:
        try:
            plan_status_monitor()
        except Exception as e:
            logger.error(f"计划状态同步异常:{e}")
        try:
            MesUpClient.sync()
        except Exception as e:
            logger.error(f"群控至MES上行异常:{e}")
        try:
            hf_trains_up()
        except Exception as e:
            print(e)
            logger.error(e)
        try:
            consume_data_up()
        except Exception as e:
            print(e)
            logger.error(e)
        time.sleep(5)

if __name__ == "__main__":
    run()