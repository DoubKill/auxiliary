# -*- coding: UTF-8 -*-
"""
auther: liwei
datetime: 2020/8/8
name: 生产数据模拟脚本
"""
import datetime
import time as t
import os
import random
import uuid
import django



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from plan.models import ProductClassesPlan, ProductDayPlan
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, ExpendMaterial, PlanStatus

pallet_count = 5

class ProductDataEmulator():

    def __init__(self, *args, **kwargs):
        self.plan_train = kwargs.get("plan_train")

    @staticmethod
    def init_datatable(self):
        pass




def gen_uuid():
    return str(uuid.uuid1())


def run():
    TrainsFeedbacks.objects.all().delete()
    PalletFeedbacks.objects.all().delete()
    EquipStatus.objects.all().delete()
    ExpendMaterial.objects.all().delete()
    day_plan_set = ProductDayPlan.objects.filter(delete_flag=False)
    for day_plan in list(day_plan_set):
        class_plan_set = ProductClassesPlan.objects.filter(product_day_plan=day_plan.id)
        pbd_set = day_plan.product_batching.batching_details.all()
        weight_list = []
        bath_no = 1
        for class_plan in list(class_plan_set):
            plan_trains = class_plan.plan_trains
            start_time = class_plan.work_schedule_plan.start_time
            for m in range(1, int(plan_trains)+1):
                class_name = class_plan.work_schedule_plan.classes.global_name
                equip_no = day_plan.equip.equip_no
                product_no = day_plan.product_batching.stage_product_batch_no
                plan_weight = class_plan.weight
                end_time = start_time + datetime.timedelta(seconds=150)
                train_data = {
                    "plan_classes_uid": class_plan.plan_classes_uid,
                    "plan_trains": plan_trains,
                    "actual_trains": m,
                    "bath_no": bath_no,
                    "equip_no": equip_no,
                    "product_no": product_no,
                    "plan_weight": plan_weight,
                    "actual_weight": m*5,
                    "begin_time": start_time,
                    "end_time": end_time,
                    "operation_user": "string-user",
                    "classes": class_name,
                    "product_time": end_time,
                }
                plan_status_data = {
                    "plan_classes_uid": class_plan.plan_classes_uid,
                    "status": "运行中",
                    "actual_trains": m,
                    "equip_no": equip_no,
                    "product_no": product_no,
                    "operation_user": "string-user",
                    "product_time": end_time,
                }
                for pbd in pbd_set:
                    weight_data = {
                        "plan_classes_uid": class_plan.plan_classes_uid,
                        "equip_no": equip_no,
                        "product_no": product_no,
                        "trains": m,
                        "plan_weight": pbd.actual_weight,
                        "actual_weight": pbd.actual_weight + pbd.standard_error,
                        "material_no": pbd.material.material_no,
                        "material_type": pbd.material.material_type.global_name,
                        "material_name": pbd.material.material_name,
                        "product_time": end_time
                    }
                    weight_list.append(ExpendMaterial(**weight_data))
                start_time = end_time
                ExpendMaterial.objects.bulk_create(weight_list)
                TrainsFeedbacks.objects.create(**train_data)
                PlanStatus.objects.create(**plan_status_data)
                if m % pallet_count == 0:
                    end_time = start_time + datetime.timedelta(seconds=150*5)
                    pallet_data = {
                            "plan_classes_uid": class_plan.plan_classes_uid,
                            "bath_no": bath_no,
                            "equip_no": equip_no,
                            "product_no": product_no,
                            "plan_weight": plan_weight*5,
                            "actual_weight": m*5*5,
                            "begin_time": start_time,
                            "end_time": end_time,
                            "operation_user": "string-user",
                            "begin_trains": m - (pallet_count-1),
                            "end_trains": m,
                            "pallet_no": f"{bath_no}|test",
                            "classes": class_name,
                            "lot_no": "我是测试条码",
                            "product_time": end_time,
                        }
                    start_time = end_time
                    bath_no += 1
                    PalletFeedbacks.objects.create(**pallet_data)
                for x in range(5):
                    equip_status_data = {
                        "plan_classes_uid": class_plan.plan_classes_uid,
                        "equip_no": equip_no,
                        "temperature": random.randint(1,200),
                        "rpm": random.randint(1,200),
                        "energy": random.randint(10,200),
                        "power": random.randint(10,2500),
                        "pressure": random.randint(2,200),
                        "status": "running",
                        "current_trains": m,
                        "product_time": end_time,
                    }
                    end_time += datetime.timedelta(seconds=1)
                    EquipStatus.objects.create(**equip_status_data)

if __name__ == '__main__':
    run()