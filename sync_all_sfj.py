# -*- coding: UTF-8 -*-
"""
auther:
datetime: 2020/11/30
name:
"""
import os
import django
import datetime
import logging

from django.db.transaction import atomic

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from mes.settings import DATABASES
from plan.models import ProductClassesPlan, ProductDayPlan
from recipe.models import ProductBatching, ProductInfo, ProductProcess, ProductProcessDetail, BaseCondition, BaseAction, \
    ProductBatchingDetail, Material
from work_station.models import SfjRecipeCon, SfjRecipeMix, SfjRecipeCb, SfjRecipeOil1, SfjRecipeGum, SfjProducePlan
from basics.models import PlanSchedule, WorkSchedule, GlobalCode, WorkSchedulePlan, Equip


logger = logging.getLogger("sync.log")

def sync_recipe_mix(db, pb, recipe_name):
    pb.process_details.all().filter().update(delete_flag=True)
    mix_set = SfjRecipeMix.objects.using(db).filter(recipe_name=recipe_name)
    for mix in mix_set:
        ProductProcessDetail.objects.create(
            product_batching=pb,
            temperature=mix.set_temp,
            condition=BaseCondition.objects.filter(condition=mix.set_condition).first(),
            action=BaseAction.objects.get(action=mix.act_code),
            rpm=mix.set_rota,
            energy=mix.set_ener,
            power=mix.set_power,
            pressure=mix.set_press,
            time=mix.set_time,
            sn=mix.ID_step
        )
    mix_set.update(flag=2)


def sync_gum(db, pb, recipe_name):
    pb.batching_details.all().filter(type=1).update(delete_flag=True)
    gum_set = SfjRecipeGum.objects.using(db).filter(matname=recipe_name)
    for gum in gum_set:
        ProductBatchingDetail.objects.create(
            product_batching=pb,
            sn=gum.act_code,
            material=Material.objects.filter(material_name=gum.matname).first(),
            actual_weight=gum.set_weight,
            standard_error=gum.error_allow,
            auto_flag=1,
            type=1
        )
    gum_set.update(flag=2)


def sync_cb(db, pb, recipe_name):
    pb.batching_details.all().filter(type=2).update(delete_flag=True)
    cb_set = SfjRecipeCb.objects.using(db).filter(matname=recipe_name)
    for gum in cb_set:
        ProductBatchingDetail.objects.create(
            product_batching=pb,
            sn=gum.act_code,
            material=Material.objects.filter(material_name=gum.matname).first(),
            actual_weight=gum.set_weight,
            standard_error=gum.error_allow,
            auto_flag=1,
            type=2
        )
    cb_set.update(flag=2)


def sync_oil1(db, pb, recipe_name):
    pb.batching_details.all().filter(type=3).update(delete_flag=True)
    oil1_set = SfjRecipeOil1.objects.using(db).filter(matname=recipe_name)
    for gum in oil1_set:
        ProductBatchingDetail.objects.create(
            product_batching=pb,
            sn=gum.act_code,
            material=Material.objects.filter(material_name=gum.matname).first(),
            actual_weight=gum.set_weight,
            standard_error=gum.error_allow,
            auto_flag=1,
            type=3
        )
    oil1_set.update(flag=2)


def sync_plan(db, pb):
    plan_set = SfjProducePlan.objects.using(db).filter(flag=1)
    equip = Equip.objects.get(equip_no=db)
    # 8-20  20-8
    #  早    夜
    # 1、根据时间和班次判断工厂时间（这一块比较重要，如何根据时间和班次找到他的工厂时间）
    for plan in plan_set:
        actual_times = plan.latesttime
        classes = plan.grouptime
        group = plan.groupoper
        h = int(actual_times.strftime("%H"))
        times = actual_times.strftime("%Y-%m-%d")
        if classes in ["夜班", "夜班"]:
            if 0 < h < 8:
                times = (actual_times + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
        # 2、代码核心（这里应该没啥子问题）
        gc_obj = GlobalCode.objects.filter(global_name='密炼工序').first()
        # 根据密炼工序找到work_schedule 总感觉通过密炼工序找work_schedule有点不对劲
        ws_obj = WorkSchedule.objects.filter(work_procedure=gc_obj, schedule_name="三班两运转").last()
        # 根据work_schedule和时间找到plan_schedule
        ps_obj = PlanSchedule.objects.filter(day_time=times, work_schedule=ws_obj).last()

        # 根据班次 班组和plan_schedule找到唯一一条work_schedule_plan
        wsp_classes = GlobalCode.objects.filter(global_name=classes).first()
        wsp_group = GlobalCode.objects.filter(global_name=group).first()
        wsp_obj = WorkSchedulePlan.objects.filter(classes=wsp_classes, plan_schedule=ps_obj, group=wsp_group).first()
        ProductClassesPlan.objects.create(product_day_plan=ProductDayPlan.objects.create(equip=equip,
                                                                                         product_batching=pb,
                                                                                         plan_schedule=ps_obj),
                                          sn=1,
                                          plan_trains=plan.setno,
                                          weight=0,  # 参考创建计划那部分代码
                                          unit="kg",
                                          work_schedule_plan=wsp_obj,
                                          plan_classes_uid=plan.planid,
                                          equip=equip,
                                          product_batching=pb
                                          )
    plan_set.update(flag=2)


@atomic
def sync_recipe(db):
    factory = GlobalCode.objects.get(global_name='安吉')
    recipe_set = SfjRecipeCon.objects.using(db).filter(flag=1)
    equip = Equip.objects.get(equip_no=db)
    for recipe in recipe_set:
        recipe_name = recipe.recipe_name
        product_info = recipe_name.split('-')
        pb_set = ProductBatching.objects.filter(used_type=4, batching_type=1,
                                                stage_product_batch_no=recipe_name,
                                                equip__equip_no=db)
        if not pb_set.exists():
            pb = ProductBatching.objects.create(
                factory=factory,
                site=GlobalCode.objects.get(global_name=product_info[0]),
                product_info=ProductInfo.objects.get_or_create(product_name=product_info[2],
                                                               product_no=product_info[2])[0],
                stage_product_batch_no=recipe_name,
                dev_type=equip.category,
                stage=GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次'),
                equip=equip,
                versions=product_info[3]
            )
        else:
            pb = pb_set.last()
            pb.factory = factory
            pb.site = GlobalCode.objects.get(global_name=product_info[0])
            pb.product_info = ProductInfo.objects.get_or_create(product_name=product_info[2],
                                                                product_no=product_info[2])[0]
            pb.stage = GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次')
            pb.dev_type = equip.category
            pb.versions = product_info[3]
            pb.save()

        ProductProcess.objects.get_or_create(
            product_batching=pb,
            equip_code=recipe.equip_code,
            mini_time=recipe.mini_time,
            max_time=recipe.max_time,
            over_time=recipe.max_time,
            mini_temp=recipe.mini_time,
            max_temp=recipe.max_temp,
            over_temp=recipe.over_temp,
            reuse_flag=False if int(recipe.if_not) == -1 else True,
            zz_temp=recipe.rot_temp,
            xlm_temp=recipe.shut_temp,
            cb_temp=recipe.side_temp,
            temp_use_flag=False if int(recipe.temp_on_off) == 1 else True,
            sp_num=2
        )
        sync_recipe_mix(db, pb, recipe_name)
        sync_gum(db, pb, recipe_name)
        sync_cb(db, pb, recipe_name)
        sync_oil1(db, pb, recipe_name)
        sync_plan(db, pb)
    recipe_set.update(flag=2)


if __name__ == '__main__':
    for db in DATABASES:
        if not db.startswith("Z"):
            continue
        else:
            # try:
            sync_recipe(db)
            # except Exception as e:
            #     print(e)
            #     logger.error(e)