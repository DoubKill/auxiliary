import datetime
import json
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from django.db.models import Sum, Max, F, Value, CharField
from django.db.models.functions import Concat
from rest_framework_extensions.cache.decorators import get_cache

from basics.models import Equip
from plan.models import ProductClassesPlan
from production.models import TrainsFeedbacks, EquipStatus

if __name__ == '__main__':
    cache = get_cache("default")
    equip_nos = Equip.objects.filter(use_flag=True, category__equip_type__global_name="密炼设备").order_by(
        'equip_no').values_list('equip_no', flat=True)

    # 计划数据，根据设备机台号和班次分组，
    plan_set = ProductClassesPlan.objects.filter(
        work_schedule_plan__plan_schedule__day_time=datetime.datetime.now().date(),
        product_day_plan__equip__equip_no__in=list(equip_nos),
        delete_flag=False
    )
    plan_data = plan_set.values('work_schedule_plan__classes__global_name',
                                'product_day_plan__equip__equip_no').annotate(plan_num=Sum('plan_trains'))
    plan_uid = plan_set.values_list("plan_classes_uid", flat=True)
    plan_data = {
        item['product_day_plan__equip__equip_no'] + item['work_schedule_plan__classes__global_name']: item
        for item in plan_data}

    # 先按照计划uid分组，取出最大的一条实际数据
    max_ids = TrainsFeedbacks.objects.filter(
        # created_date__date=datetime.datetime.now().date(),
        plan_classes_uid__in=plan_uid
    ).values('plan_classes_uid').annotate(max_id=Max('id')).values_list('max_id', flat=True)
    # 实际数据，根据设备机台号和班次分组，
    actual_data = TrainsFeedbacks.objects.filter(
        id__in=max_ids).values('equip_no', 'classes').annotate(
        actual_num=Sum('actual_trains'),
        ret=Max(Concat(F('equip_no'), Value(","),
                       F('created_date'), Value(","),
                       F('product_no'), output_field=CharField()
                       )))
    actual_data = {item['equip_no'] + item['classes']: item for item in actual_data}

    # 机台反馈数据
    equip_status_data = EquipStatus.objects.filter(
        created_date__date=datetime.datetime.now().date()
    ).values('equip_no').annotate(ret=Max(Concat(F('equip_no'), Value(","),
                                                 F('created_date'), Value(","),
                                                 F('current_trains'), Value(','),
                                                 F('status')), output_field=CharField()))
    equip_status_data = {item['equip_no']: item for item in equip_status_data}

    ret_data = {item: [] for item in equip_nos}

    class_dict = {'早班': 1, '中班': 2, '夜班': 3}
    for key, value in plan_data.items():
        class_name = value['work_schedule_plan__classes__global_name']
        equip_no = value['product_day_plan__equip__equip_no']
        classes_id = class_dict[class_name]
        plan_num = value['plan_num']
        if key in actual_data:
            actual_ret = actual_data[key]['ret'].split(',')
            actual_num = actual_data[key]['actual_num']
            es_ret = None
            if equip_no in equip_status_data:
                es_ret = equip_status_data[equip_no]['ret'].split(',')
            ret_data[equip_no].append(
                {"classes_id": classes_id,
                 "global_name": class_name,
                 "plan_num": plan_num,
                 "actual_num": actual_num,
                 'ret': [actual_ret[2], es_ret[2], es_ret[3]] if es_ret else [actual_ret[2], '--', '--']
                 }
            )
        else:
            ret_data[equip_no].append(
                {"classes_id": classes_id,
                 "global_name": class_name,
                 "plan_num": plan_num,
                 "actual_num": 0,
                 'ret': []
                 }
            )
        response_triple = (
            json.dumps(ret_data).encode("utf-8"),
            200,
            {'content-type': ('Content-Type', 'application/json'), 'vary': ('Vary', 'Accept'), 'allow': ('Allow', 'GET, HEAD, OPTIONS')}
        )
        cache.set("1d1947aa64c62ccba4b27ada9b0e9cba", response_triple, 600)