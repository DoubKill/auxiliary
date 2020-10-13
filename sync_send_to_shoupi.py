import functools
import logging
import os
import socket
import time

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from collections import OrderedDict
from production.utils import strtoint
from rest_framework.exceptions import ValidationError

from mes.common_code import WebService
from plan.models import ProductClassesPlan
from work_station.models import IfupReportBasis
from production.models import PlanStatus, TrainsFeedbacks
from work_station import models as md

logger = logging.getLogger('send_log')


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
            logger.info('already has an instance, this script will not be excuted')
            return
        return func(*args,**kwargs)
    return f


def send_to_yikong_run():
    """下达计划"""
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + str(ext_str))
        plan_obj = model_name.objects.filter().first()
        if plan_obj:
            if plan_obj.recstatus in ["等待", "运行中"]:
                plan_id = plan_obj.planid
                # 查出对应计划的历史状态
                pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=plan_id).values(
                    'product_day_plan__product_batching__stage_product_batch_no',
                    'work_schedule_plan__plan_schedule__day_time', 'plan_classes_uid', 'work_schedule_plan__start_time',
                    'work_schedule_plan__end_time', 'work_schedule_plan__classes__global_name',
                    'work_schedule_plan__group__global_name', 'plan_trains', 'created_user__username',
                    'product_day_plan__equip__equip_no', 'product_day_plan__product_batching__batching_weight',
                    'product_day_plan__product_batching__processes__sp_num')
                if pcp_obj:
                    # 计划下达到易控组态
                    test_dict = OrderedDict()  # 传给易控组态的数据
                    test_dict['recipe_name'] = pcp_obj[0].get(
                        "product_day_plan__product_batching__stage_product_batch_no", "")
                    test_dict['recipe_code'] = pcp_obj[0].get(
                        "product_day_plan__product_batching__stage_product_batch_no", "")
                    test_dict['latesttime'] = str(pcp_obj[0].get("work_schedule_plan__plan_schedule__day_time", ""))
                    test_dict['planid'] = pcp_obj[0].get("plan_classes_uid", "")
                    test_dict['starttime'] = str(pcp_obj[0].get("work_schedule_plan__start_time", ""))
                    test_dict['stoptime'] = str(pcp_obj[0].get("work_schedule_plan__end_time", ""))
                    test_dict['grouptime'] = pcp_obj[0].get("work_schedule_plan__classes__global_name", "")
                    test_dict['groupoper'] = pcp_obj[0].get("work_schedule_plan__group__global_name", "")
                    test_dict['setno'] = pcp_obj[0].get("plan_trains", 0)
                    test_dict['oper'] = pcp_obj[0].get("created_user__username", "")
                    test_dict['runstate'] = "运行中"  # '运行中'
                    test_dict['machineno'] = strtoint(
                        pcp_obj[0].get("product_day_plan__equip__equip_no", 0))  # 易控组态那边的机台euqip_no是int类型
                    tfb_obj = TrainsFeedbacks.objects.filter(
                        plan_classes_uid=pcp_obj[0].get("plan_classes_uid")).order_by(
                        'created_date').last()
                    if tfb_obj:
                        test_dict['finishno'] = tfb_obj.actual_trains
                    else:
                        test_dict['finishno'] = 0
                    test_dict['weight'] = pcp_obj[0].get("product_day_plan__product_batching__batching_weight", "")

                    test_dict['sp_number'] = pcp_obj[0].get("product_day_plan__product_batching__processes__sp_num", "")
                    try:
                        WebService.issue(test_dict, 'plan')
                    except Exception as e:
                        raise ValidationError(f"收皮机连接超时|{e}")


def send_to_yikong_stop():
    """计划停止"""
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + str(ext_str))
        plan_obj = model_name.objects.filter(recstatus__in=["停止", "完成"]).first()
        if plan_obj:
            plan_id = plan_obj.planid
            actual = IfupReportBasis.objects.filter(计划号=plan_id).last()  # 获取当前计划的最新车次
            target = TrainsFeedbacks.objects.filter(plan_classes_uid=plan_id).last()  # 获取群控系统的最新车次
            if actual and target:
                if target.actual_trains == actual.车次号:
                    test_dict = OrderedDict()
                    test_dict['stopstate'] = '停止'
                    test_dict['planid'] = plan_obj.planid
                    test_dict['no'] = ext_str
                    try:
                        WebService.issue(test_dict, 'stop')
                    except Exception as e:
                        raise ValidationError(f"收皮机连接超时|{e}")


def send_to_yikong_update():
    """更新车次"""
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + str(ext_str))
        scjh_set = model_name.objects.filter(recstatus__in=['车次需更新', "配方车次需更新"])
        if not scjh_set:
            pass
        else:
            for scjh_obj in scjh_set:
                test_dict = OrderedDict()
                test_dict['updatestate'] = scjh_obj.setno
                test_dict['planid'] = scjh_obj.planid
                test_dict['no'] = ext_str
                try:
                    WebService.issue(test_dict, 'updatetrains')
                except Exception as e:
                    raise ValidationError(f"收皮机连接超时|{e}")


def send_again_yikong_again():
    """配方重传"""
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + str(ext_str))
        scjh_set = model_name.objects.filter(recstatus__in=["配方需重传", "配方车次需更新"])
        if not scjh_set:
            pass
        else:
            for scjh_obj in scjh_set:
                test_dict = OrderedDict()  # 传给易控组态的数据
                test_dict['planid'] = scjh_obj.planid
                pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=scjh_obj.planid).first()
                weight = pcp_obj.product_day_plan.product_batching.batching_weight
                if weight:
                    test_dict['weight'] = pcp_obj.product_day_plan.product_batching.batching_weight
                else:
                    test_dict['weight'] = 0
                sp_number = pcp_obj.product_day_plan.product_batching.processes.sp_num
                if sp_number:
                    test_dict['sp_number'] = pcp_obj.product_day_plan.product_batching.processes.sp_num
                else:
                    test_dict['sp_number'] = 0
                # test_dict['runstate'] = "运行中"  # '运行中'
                test_dict['no'] = ext_str
                try:
                    WebService.issue(test_dict, 'planAgain')
                except Exception as e:
                    raise ValidationError(f"超时链接|{e}")

@one_instance
def run():
    logger.info("向收皮机发送数据")
    while True:
        # 防止报错之后脚本就直接停了
        # 计划下达
        for fun in [send_to_yikong_run, send_to_yikong_stop, send_to_yikong_update, send_again_yikong_again]:
            try:
                fun()
            except Exception as e:
                logger.error(f"{fun.__doc__}|{e}")

        time.sleep(5)  # 目前设为10秒一次 因为向收皮机发送请求设置timeout是3秒


if __name__ == "__main__":
    run()
