import traceback

import xlrd
from django.db.transaction import atomic

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from basics.models import GlobalCode, Equip
from recipe.models import Material, ProductProcess, ProductBatching, ProductInfo, ProductBatchingDetail, \
    ProductProcessDetail, BaseCondition, BaseAction


@atomic()
def read_material_excel_data():
    data = xlrd.open_workbook('recipe.xls')
    table = data.sheet_by_name('原材料')
    for rowNum in range(1, table.nrows):
        value = table.row_values(rowNum)
        material_name = value[2].strip()
        material_no = value[3].strip()
        if material_no.startswith('A') or not material_no:
            material_type_id = GlobalCode.objects.get(global_name='天然胶', global_type__type_name='原材料类别').id
        elif material_no.startswith('B'):
            material_type_id = GlobalCode.objects.get(global_name='合成胶', global_type__type_name='原材料类别').id
        elif material_no.startswith('C'):
            material_type_id = GlobalCode.objects.get(global_name='炭黑', global_type__type_name='原材料类别').id
        elif material_no.startswith('F'):
            material_type_id = GlobalCode.objects.get(global_name='白色填料', global_type__type_name='原材料类别').id
        elif material_no.startswith('L'):
            material_type_id = GlobalCode.objects.get(global_name='防老剂', global_type__type_name='原材料类别').id
        elif material_no.startswith('M'):
            material_type_id = GlobalCode.objects.get(global_name='再生胶', global_type__type_name='原材料类别').id
        elif material_no.startswith('P'):
            material_type_id = GlobalCode.objects.get(global_name='增塑剂', global_type__type_name='原材料类别').id
        elif material_no.startswith('R'):
            material_type_id = GlobalCode.objects.get(global_name='粘合剂', global_type__type_name='原材料类别').id
        elif material_no.startswith('S'):
            material_type_id = GlobalCode.objects.get(global_name='活化剂', global_type__type_name='原材料类别').id
        elif material_no.startswith('T'):
            material_type_id = GlobalCode.objects.get(global_name='树脂', global_type__type_name='原材料类别').id
        else:
            material_type_id = GlobalCode.objects.get(global_name='其他化工类', global_type__type_name='原材料类别').id
        if not material_no:
            material_no = material_name
        try:
            if Material.objects.filter(material_no=material_no,
                                       material_name=material_name).exists():
                continue
            else:
                Material.objects.get_or_create(material_no=material_no,
                                               material_name=material_name,
                                               material_type_id=material_type_id)
        except Exception:
            print(traceback.format_exc())
            raise


@atomic()
def read_product_process():
    data = xlrd.open_workbook('recipe.xls')
    table = data.sheet_by_name('配方步序')
    factory = GlobalCode.objects.get(global_name='安吉')
    equip = Equip.objects.get(equip_no='Z06')
    for rowNum in range(1, table.nrows):
        try:
            value = table.row_values(rowNum)
            product_name = value[4].strip()
            product_batching = ProductBatching.objects.filter(equip=equip,
                                                              stage_product_batch_no=product_name).first()
            if not product_batching:
                product_info = product_name.split('-')
                if not len(product_info) > 2:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        equip=equip
                    )
                else:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        site=GlobalCode.objects.get(global_name=product_info[0]),
                        product_info=ProductInfo.objects.get_or_create(product_name=product_info[2],
                                                                       product_no=product_info[2])[0],
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        stage=GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次'),
                        equip=equip,
                        versions=product_info[3]
                    )
            ProductProcess.objects.get_or_create(
                product_batching=product_batching,
                equip_code=value[5],
                mini_time=value[7],
                max_time=value[8],
                over_time=value[8],
                mini_temp=value[9],
                max_temp=value[10],
                over_temp=value[11],
                reuse_flag=False if int(value[12]) == -1 else True,
                zz_temp=value[13],
                xlm_temp=value[14],
                cb_temp=value[15],
                temp_use_flag=False if int(value[16]) == 1 else True,
                sp_num=2
            )
        except Exception:
            print(traceback.format_exc())
            raise


@atomic()
def read_product_batching():
    data = xlrd.open_workbook('recipe.xls')
    table = data.sheet_by_name('配料详情')
    factory = GlobalCode.objects.get(global_name='安吉')
    equip = Equip.objects.get(equip_no='Z06')
    for rowNum in range(1, table.nrows):
        try:
            value = table.row_values(rowNum)
            product_name = value[1].strip()
            product_batching = ProductBatching.objects.filter(equip=equip,
                                                              stage_product_batch_no=product_name).first()
            if not product_batching:
                product_info = product_name.split('-')
                if not len(product_info) > 2:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        equip=equip
                    )
                else:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        site=GlobalCode.objects.get(global_name=product_info[0]),
                        product_info=ProductInfo.objects.get_or_create(product_name=product_info[2],
                                                                       product_no=product_info[2])[0],
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        stage=GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次'),
                        equip=equip,
                        versions=product_info[3]
                    )
            ProductBatchingDetail.objects.create(
                product_batching=product_batching,
                sn=1,
                material=Material.objects.filter(material_name=value[3]).first(),
                actual_weight=value[4],
                standard_error=value[5],
                auto_flag=1,
                type=1
            )
        except Exception:
            print(traceback.format_exc())
            raise

    for product_batch in ProductBatching.objects.all():
        i = 1
        for product_batch_detail in product_batch.batching_details.all():
            product_batch_detail.sn = i
            product_batch_detail.save()
            i += 1
            product_batch.batching_weight += product_batch_detail.actual_weight
        product_batch.save()


@atomic()
def read_product_process_detail():
    data = xlrd.open_workbook('recipe.xls')
    table = data.sheet_by_name('配方步序详情')
    factory = GlobalCode.objects.get(global_name='安吉')
    equip = Equip.objects.get(equip_no='Z06')
    for rowNum in range(1, table.nrows):
        try:
            value = table.row_values(rowNum)
            product_name = value[1].strip()
            product_batching = ProductBatching.objects.filter(equip=equip,
                                                              stage_product_batch_no=product_name).first()
            if not product_batching:
                product_info = product_name.split('-')
                if not len(product_info) > 2:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        equip=equip
                    )
                else:
                    product_batching = ProductBatching.objects.create(
                        factory=factory,
                        site=GlobalCode.objects.get(global_name=product_info[0]),
                        product_info=ProductInfo.objects.get_or_create(product_name=product_info[2],
                                                                       product_no=product_info[2])[0],
                        stage_product_batch_no=product_name,
                        dev_type=equip.category,
                        stage=GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次'),
                        equip=equip,
                        versions=product_info[3]
                    )
            ProductProcessDetail.objects.create(
                product_batching=product_batching,
                temperature=value[4],
                condition=BaseCondition.objects.filter(condition=value[2]).first(),
                action=BaseAction.objects.get(action=value[7]),
                rpm=value[8],
                energy=value[5],
                power=value[6],
                pressure=value[9],
                time=value[3],
                sn=value[10]
            )
        except Exception:
            print(traceback.format_exc())
            raise


if __name__ == '__main__':
    read_material_excel_data()
    read_product_process()
    read_product_batching()
    read_product_process_detail()