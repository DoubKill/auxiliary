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
    ps_set = PlanStatus.objects.filter(status='已下达')
    if ps_set:
        for ps_obj in ps_set:
            pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=ps_obj.plan_classes_uid).values(
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
                    success_flag = WebService.issue(test_dict, 'plan')
                    if not success_flag:
                        raise ValidationError("收皮机错误")
                except Exception as e:
                    raise ValidationError("收皮机连接超时")
            else:
                pass
    else:
        pass


def send_to_yikong_stop():
    # 发送数据给易控
    ps_set = PlanStatus.objects.filter(status='待停止')
    if ps_set:
        for ps_obj in ps_set:
            test_dict = OrderedDict()
            test_dict['stopstate'] = '停止'
            test_dict['planid'] = ps_obj.plan_classes_uid
            try:
                success_flag = WebService.issue(test_dict, 'stop')
                if not success_flag:
                    raise ValidationError("收皮机错误")
            except Exception as e:
                raise ValidationError("收皮机连接超时")
    else:
        pass


def send_to_yikong_update():
    # 更新车次
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + ext_str)
        scjh_set = model_name.objects.filter(recstatus__in=['车次需更新', "配方车次需更新"])
        if not scjh_set:
            pass
        else:
            for scjh_obj in scjh_set:
                test_dict = OrderedDict()
                test_dict['updatestate'] = scjh_obj.actno
                test_dict['planid'] = scjh_obj.planid
                try:
                    success_flag = WebService.issue(test_dict, 'updatetrains')
                    if not success_flag:
                        raise ValidationError("收皮机错误")
                except Exception as e:
                    raise ValidationError("收皮机连接超时")


def send_again_yikong_again():
    # 计划下达到易控组态
    model_list = 'IfdownShengchanjihua'
    ext_str_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    for ext_str in ext_str_list:
        model_name = getattr(md, model_list + ext_str)
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
                test_dict['runstate'] = "运行中"  # '运行中'
                try:
                    success_flag = WebService.issue(test_dict, 'planAgain')
                    if success_flag:
                        return True
                    else:
                        raise ValidationError("未知错误")
                except Exception as e:
                    raise ValidationError("超时链接")

@one_instance
def run():
    logger.info("向收皮机发送数据")
    while True:
        # 防止报错之后脚本就直接停了
        # 计划下达
        try:
            send_to_yikong_run()
        except Exception as e:
            logger.info("计划下达错误:{}".format(e))
            pass
        # 计划停止
        try:
            send_to_yikong_stop()
        except Exception as e:
            logger.info("计划停止错误:{}".format(e))
            pass
        # 修改车次
        try:
            send_to_yikong_update()
        except Exception as e:
            logger.info("修改车次错误:{}".format(e))
            pass
        # 计划重传
        try:
            send_again_yikong_again()
        except Exception as e:
            logger.info("计划重传错误:{}".format(e))
            pass

        time.sleep(10)  # 目前设为10秒一次 因为向收皮机发送请求设置timeout是3秒


if __name__ == "__main__":
    run()
