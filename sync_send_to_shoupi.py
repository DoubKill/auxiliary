"""
    向戴工收皮系统发送计划数据、更新计划车次、更新计划状态
    ！！！已改成定时任务，每分钟跑一次
"""

import logging
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from collections import OrderedDict
from production.utils import strtoint
from work_station.models import I_ORDER_STATE_V
from mes.common_code import WebService
from plan.models import ProductClassesPlan
from production.models import TrainsFeedbacks

logger = logging.getLogger('send_log')


# def one_instance(func):
#     '''
#     如果已经有实例在跑则退出
#     '''
#     @functools.wraps(func)
#     def f(*args,**kwargs):
#         try:
#         # 全局属性，否则变量会在方法退出后被销毁
#             global s
#             s = socket.socket()
#             host = socket.gethostname()
#             s.bind((host, 60124))
#         except:
#             logger.info('already has an instance, this script will not be excuted')
#             return
#         return func(*args,**kwargs)
#     return f


def send_to_yikong_run():
    """下达计划"""
    plan_obj = I_ORDER_STATE_V.objects.using("H-Z04").filter(order_status="PRODUCTION").order_by("order_start_date").last()
    if plan_obj:
        plan_id = plan_obj.order_name
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
                plan_classes_uid=pcp_obj[0].get("plan_classes_uid")).order_by('id').last()
            if tfb_obj:
                test_dict['finishno'] = tfb_obj.actual_trains
            else:
                test_dict['finishno'] = 0
            recipe_weight = pcp_obj[0].get("product_day_plan__product_batching__batching_weight", 220)
            test_dict['weight'] = recipe_weight
            test_dict['sp_number'] = 750 // recipe_weight
            try:
                WebService.issue(test_dict, 'plan', equip_no="4")
            except Exception as e:
                logger.error(f"Z04计划下达失败：超时链接|{e}")

            sfj_plan_trains = pcp_obj[0].get("plan_trains", 0)
            z04_plan_trains = plan_obj.batches_set
            if sfj_plan_trains != z04_plan_trains:
                test_dict2 = OrderedDict()
                test_dict2['updatestate'] = z04_plan_trains
                test_dict2['planid'] = plan_obj.order_name
                test_dict2['no'] = 4
                try:
                    WebService.issue(test_dict2, 'updatetrains', equip_no="4")
                except Exception as e:
                    logger.error(f"Z04更新计划失败,超时链接|{e}")
                pcp = ProductClassesPlan.objects.filter(plan_classes_uid=plan_id).first()
                pcp.plan_trains = z04_plan_trains
                pcp.save()


def send_to_yikong_stop():
    """计划停止"""
    plan_obj = I_ORDER_STATE_V.objects.using("H-Z04").filter(order_status="UNFINISHED").order_by("order_start_date").last()
    if plan_obj:
        test_dict = OrderedDict()
        test_dict['stopstate'] = '停止'
        test_dict['planid'] = plan_obj.order_name
        test_dict['no'] = 4
        try:
            WebService.issue(test_dict, 'stop', equip_no='4')
        except Exception as e:
            logger.error(f"Z04超时链接|{e}")


# def send_to_yikong_update():
#     """更新车次"""
#     plan = I_ORDER_STATE_V.objects.using("H-Z04").filter(order_status="PRODUCTION").order_by("order_start_date").last()
#     if not plan:
#         pass
#     else:
#         pcp = ProductClassesPlan.objects.get(plan_classes_uid=plan.order_name)
#         plan_trains = pcp.plan_trains
#         if plan_trains != plan.batches_set:
#             test_dict = OrderedDict()
#             test_dict['updatestate'] = plan.batches_set
#             test_dict['planid'] = plan.order_name
#             test_dict['no'] = 4
#             try:
#                 WebService.issue(test_dict, 'updatetrains', equip_no="4")
#             except Exception as e:
#                 logger.error(f"Z04超时链接|{e}")
#             else:
#                 pcp.plan_trains = plan.batches_set
#                 pcp.save()


# def send_again_yikong_again():
#     """配方重传"""
#     model_list = 'IfdownShengchanjihua'
#     ext_str_list = [6, 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15]
#     for ext_str in ext_str_list:
#         model_name = getattr(md, model_list + str(ext_str))
#         scjh_set = model_name.objects.filter(recstatus__in=["配方需重传", "配方车次需更新"])
#         if not scjh_set:
#             pass
#         else:
#             for scjh_obj in scjh_set:
#                 test_dict = OrderedDict()  # 传给易控组态的数据
#                 test_dict['planid'] = scjh_obj.planid
#                 pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=scjh_obj.planid).first()
#                 weight = pcp_obj.product_day_plan.product_batching.batching_weight
#                 if weight:
#                     test_dict['weight'] = pcp_obj.product_day_plan.product_batching.batching_weight
#                 else:
#                     test_dict['weight'] = 0
#                 sp_number = pcp_obj.product_day_plan.product_batching.processes.sp_num
#                 if sp_number:
#                     test_dict['sp_number'] = pcp_obj.product_day_plan.product_batching.processes.sp_num
#                 else:
#                     test_dict['sp_number'] = 0
#                 # test_dict['runstate'] = "运行中"  # '运行中'
#                 test_dict['no'] = ext_str
#                 try:
#                     WebService.issue(test_dict, 'planAgain', equip_no=ext_str)
#                 except Exception as e:
#                     logger.error(f"{ext_str}超时链接|{e}")

# @one_instance
# def run():
#     logger.info("向收皮机发送数据")
#     while True:
#         # 防止报错之后脚本就直接停了
#         # 计划下达
#         for fun in [send_to_yikong_run, send_to_yikong_stop, send_to_yikong_update]:
#             try:
#                 fun()
#             except Exception as e:
#                 logger.error(f"{fun.__doc__}|{e}")
#                 # print(f"{fun.__doc__}|{e}")
#
#         time.sleep(5)  # 目前设为10秒一次 因为向收皮机发送请求设置timeout是3秒
#

if __name__ == "__main__":
    send_to_yikong_run()
    send_to_yikong_stop()