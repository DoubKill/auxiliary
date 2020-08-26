from django.test import TestCase

# Create your tests here.
import datetime
import time as t
import os
import random
import uuid
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from plan.models import ProductClassesPlan
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, IfupReportBasisBackups, \
    IfupReportWeightBackups, IfupReportMixBackups, IfupReportCurveBackups
from system.models import User
from work_station.models import IfupReportBasis, IfupReportCurve, IfupReportMix
from django.db.transaction import atomic
from production.utils import strtoint


def random_name():
    user_dict = User.objects.values('username')
    name_list = []
    for _ in user_dict:
        name_list.append(_['username'])
    return random.choice(name_list)


def random_status():
    status_list = ['等待', '运行中', '完成']
    return random.choice(status_list)


def add_product():
    pcp_set = ProductClassesPlan.objects.all()[:3]
    for pcp_obj in pcp_set:
        num = pcp_obj.weight / pcp_obj.plan_trains
        # for i in range(1, pcp_obj.plan_trains + 1):
        for i in range(1, 3):
            t = TrainsFeedbacks.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid,
                                               plan_trains=pcp_obj.plan_trains,
                                               actual_trains=i, bath_no=i,
                                               equip_no=pcp_obj.product_day_plan.equip.equip_no,
                                               product_no=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                               plan_weight=pcp_obj.weight,
                                               actual_weight=num * i,
                                               begin_time=datetime.datetime.now(),
                                               end_time=datetime.datetime.now(),
                                               operation_user=random_name(),
                                               classes=pcp_obj.work_schedule_plan.classes.global_name)
            # 与此同时中间表增数据
            IfupReportBasisBackups.objects.create(车次号=t.plan_trains, 开始时间=t.begin_time, 消耗时间=i, 排胶时间=i,
                                                  间隔时间=i, 排胶温度=i, 排胶功率=i, 排胶能量=i, 作业方式='去你妈的作业',
                                                  控制方式='好累啊', 员工代号=random_name(), 总重量=t.plan_weight,
                                                  胶料重量=t.plan_weight, 炭黑重量=t.plan_weight, 油1重量=i, 油2重量=i,
                                                  计划号=t.plan_classes_uid, 配方号=t.product_no, 加胶时间=i, 加炭黑时间=i,
                                                  加油1时间=1, 加油2时间=i, 存盘时间=str(i), 机台号=strtoint(t.equip_no),
                                                  recstatus=random_status())
            print(t)
            p = PalletFeedbacks.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid,
                                               bath_no=i, equip_no=pcp_obj.product_day_plan.equip.equip_no,
                                               product_no=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                               plan_weight=pcp_obj.weight,
                                               actual_weight=num * i,
                                               begin_time=datetime.datetime.now(),
                                               end_time=datetime.datetime.now(),
                                               operation_user=random_name(),
                                               begin_trains=i, end_trains=1,
                                               pallet_no='托盘（虽然我也不知道是啥意思）',
                                               barcode=i * 100,
                                               classes=pcp_obj.work_schedule_plan.classes.global_name,
                                               lot_no='追踪号'
                                               )
            print(p)
            e = EquipStatus.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid,
                                           equip_no=pcp_obj.product_day_plan.equip.equip_no,
                                           temperature=36.7,
                                           rpm=1.1, energy=2.2, power=3.3, pressure=4.4, status=random_status(),
                                           current_trains=i)
            print(e)
            ps = PlanStatus.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid,
                                           equip_no=pcp_obj.product_day_plan.equip.equip_no,
                                           product_no=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                           status=random_status(), operation_user=random_name())
            print(ps)

        IfupReportWeightBackups.objects.create(车次号=t.plan_trains, 物料名称=t.product_no, 设定重量=t.plan_weight,
                                               实际重量=t.actual_weight, 秤状态='扛不住了啊', 计划号=t.plan_classes_uid,
                                               配方号=t.product_no, 物料编码='物料编码', 物料类型='类型啊~~~', 存盘时间=i,
                                               机台号=strtoint(t.equip_no), recstatus=random_status())
        IfupReportMixBackups.objects.create(步骤号=i, 条件="啥条件", 时间=i, 温度=i, 功率=i, 能量=i, 动作='铁山靠', 转速=i,
                                            压力=i, 计划号=t.plan_classes_uid, 配方号=t.product_no, 存盘时间=i, 密炼车次=i,
                                            机台号=strtoint(t.equip_no), recstatus=random_status())
        IfupReportCurveBackups.objects.create(计划号=t.plan_classes_uid, 配方号=t.product_no, 温度=i, 能量=i, 功率=i, 压力=i, 转速=i,
                                              存盘时间=i, 机台号=strtoint(t.equip_no), recstatus=random_status())


def add_work():
    pcp_set = ProductClassesPlan.objects.all()
    for pcp_obj in pcp_set:
        for i in range(1, pcp_obj.plan_trains + 1):
            i = IfupReportBasis.objects.create(车次号=i, 开始时间=i, 消耗时间=i, 排胶时间=i, 间隔时间=i, 排胶温度=i,
                                               排胶功率=i, 排胶能量=i, 作业方式="作业方式", 控制方式="控制方式",
                                               员工代号=random_name(), 总重量=pcp_obj.weight, 胶料重量=pcp_obj.weight,
                                               炭黑重量=pcp_obj.weight, 油1重量=pcp_obj.weight, 油2重量=pcp_obj.weight,
                                               计划号=pcp_obj.plan_classes_uid,
                                               配方号=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                               加胶时间=i, 加炭黑时间=i, 加油1时间=i, 加油2时间=i, 存盘时间=f'存盘时间？char? {i}',
                                               机台号=pcp_obj.product_day_plan.equip.equip_no, recstatus='不知道这是啥')
            print(i)
            ic = IfupReportCurve.objects.create(计划号=pcp_obj.plan_classes_uid,
                                                配方号=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                                温度=i, 能量=i + 1, 功率=i + 2, 压力=i + 3, 转速=i + 4, 存盘时间=f'存盘时间？char? {i}',
                                                机台号=pcp_obj.product_day_plan.equip.equip_no, recstatus='不知道这是啥')
            print(ic)
            im = IfupReportMix.objects.create(步骤号=i, 条件="任意条件", 时间=i, 温度=i, 功率=i, 能量=i, 动作="动作", 压力=i + 3, 转速=i + 4,
                                              计划号=pcp_obj.plan_classes_uid,
                                              配方号=pcp_obj.product_day_plan.product_batching.stage_product_batch_no,
                                              存盘时间=f'存盘时间？char? {i}', 密炼车次=i,
                                              机台号=pcp_obj.product_day_plan.equip.equip_no, recstatus='不知道这是啥')


if __name__ == '__main__':
    add_product()
    # add_work()
