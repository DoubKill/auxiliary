import logging
import os
import sys

import django
import requests
from django.conf import settings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from recipe.models import ProductBatching, ProductBatchingDetail, Material
from system.models import DataSynchronization
from plan.models import ProductDayPlan, ProductClassesPlan

logger = logging.getLogger('sync_log')


class BaseDownloader(object):
    path = ""
    type = ""
    upload_fields = ()
    model = ''
    filter_dict = {}
    exclude_dict = {}

    def __init__(self):
        if not all([self.path, self.type, self.upload_fields, self.model]):
            raise
        self.endpoint = settings.MES_URL
        self.session = requests.Session()
        model_type = getattr(self, 'type', None)
        self.loaded = list(DataSynchronization.objects.filter(type=model_type).values_list('obj_id', flat=True))

    def request(self, data):
        url = self.endpoint + self.path
        # data['equip__equip_no'] = data['product_day_plan__equip__equip_no']
        # data['product_batching__stage_product_batch_no'] = data['product_day_plan__product_batching__stage_product_batch_no']
        # data["status"] = "完成"
        resp = self.session.post(url, data=data)
        if resp.status_code != 201:
            raise Exception(resp.text)
        return resp.json()

    def download(self):
        ret = self.model.objects.exclude(id__in=self.loaded, **self.exclude_dict).filter(**self.filter_dict).values(
            *self.upload_fields)
        for data in ret:
            try:
                res = self.request(data)
                logger.info(res)
                DataSynchronization.objects.get_or_create(type=self.type, obj_id=data['id'])
            except Exception as e:
                logger.error('同步{}失败,  id:{},  data:{}, message:{}'.format(self.__doc__, data['id'], data, e))
                continue


class ProductBatchingDown(BaseDownloader):
    path = "api/v1/plan/product-batching-receive/"
    type = 11
    upload_fields = (
        'id', 'factory__global_no', 'site__global_no', 'product_info__product_no', 'precept', 'stage_product_batch_no',
        'dev_type__category_no', 'stage__global_no', 'versions', 'used_type', 'batching_weight',
        'manual_material_weight', 'auto_material_weight', 'volume', 'production_time_interval', 'equip__equip_no',
        'batching_type', 'delete_flag', 'created_date')
    model = ProductBatching
    filter_dict = {"batching_type": 1, "used_type": 4}


class MaterialDown(BaseDownloader):
    path = "api/v1/plan/material-receive/"
    type = 9
    upload_fields = (
        'id', 'material_no', 'material_name', 'for_short', 'material_type__global_no', 'package_unit__global_no',
        'use_flag', 'delete_flag', 'created_date')
    model = Material


class ProductBatchingDetailDown(BaseDownloader):
    path = "api/v1/plan/product-batching-detail-receive/"
    type = 12
    upload_fields = (
        'id', 'product_batching__stage_product_batch_no', 'sn', 'material__material_no', 'actual_weight',
        'standard_error',
        'auto_flag', 'type', 'delete_flag', 'created_date')
    filter_dict = {"product_batching__batching_type": 1, "product_batching__used_type": 4}
    model = ProductBatchingDetail


class ProductDayPlanDown(BaseDownloader):
    path = "api/v1/plan/product-day-plan-receive/"
    type = 13
    upload_fields = (
        'id', 'equip__equip_no', 'product_batching__stage_product_batch_no', 'plan_schedule__plan_schedule_no',
        'delete_flag', 'created_date',)
    model = ProductDayPlan


class ProductClassesPlanDown(BaseDownloader):
    path = "api/v1/plan/product-classes-plan-receive/"
    type = 14
    upload_fields = (
        'id', 'sn', 'plan_trains', 'time', 'weight', 'unit', 'work_schedule_plan__work_schedule_plan_no',
        'plan_classes_uid', 'note', 'equip__equip_no', 'product_batching__stage_product_batch_no', 'status',
        'product_day_plan__equip__equip_no', 'product_day_plan__product_batching__stage_product_batch_no',
        'product_day_plan__plan_schedule__plan_schedule_no', 'delete_flag', 'created_date')
    model = ProductClassesPlan
    # exclude_dict = {'status': '等待'}


if __name__ == '__main__':

    for downloader in (
            ProductBatchingDown, MaterialDown, ProductBatchingDetailDown, ProductDayPlanDown, ProductClassesPlanDown,
    ):
        downloader().download()
