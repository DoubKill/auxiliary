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

from django.db.models import F

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from django.db import IntegrityError
from django.db.transaction import atomic

from production.models import EquipStatus, AlarmLog, TrainsFeedbacks, PlanStatus, ExpendMaterial
from mes.settings import DATABASES
from plan.models import ProductClassesPlan, ProductDayPlan
from recipe.models import ProductBatching, ProductInfo, ProductProcess, ProductProcessDetail, BaseCondition, BaseAction, \
    ProductBatchingDetail, Material
from work_station.models import SfjRecipeCon, SfjRecipeMix, SfjRecipeCb, SfjRecipeOil1, SfjRecipeGum, SfjProducePlan, \
    SfjEquipStatus, SfjAlarmLog, BatchReport, MaterialsConsumption
from basics.models import PlanSchedule, WorkSchedule, GlobalCode, WorkSchedulePlan, Equip


logger = logging.getLogger("sync.log")

def sync_recipe_mix(db, pb, recipe_name):
    pb.process_details.all().filter().update(delete_flag=True)
    mix_set = SfjRecipeMix.objects.using(db).filter(recipe_name=recipe_name, flag=1)
    for mix in mix_set:
        try:
            ProductProcessDetail.objects.create(
                product_batching=pb,
                temperature=mix.set_temp,
                condition=BaseCondition.objects.filter(condition=mix.set_condition).first(),
                action=BaseAction.objects.get(action=mix.act_code),
                rpm=mix.set_rota,
                energy=mix.set_ener,
                power=mix.set_power,
                pressure=mix.set_pres,
                time=mix.set_time,
                sn=mix.ID_step
            )
        except Exception as e:
            logger.error("步序异常", e)
            print("步序异常", e)
            pass
        mix.flag = 2
        mix.save()


def sync_gum(db, pb, recipe_name):
    pb.batching_details.all().filter(type=1).update(delete_flag=True)
    gum_set = SfjRecipeGum.objects.using(db).filter(recipe_name=recipe_name, flag=1)
    for gum in gum_set:
        try:
            ProductBatchingDetail.objects.create(
                product_batching=pb,
                sn=gum.act_code,
                material=Material.objects.filter(material_name=gum.matname.strip()).first(),
                actual_weight=gum.set_weight,
                standard_error=gum.error_allow,
                auto_flag=1,
                type=1
            )
        except Exception as e:
            print("缺料", gum.matname)
            logger.error("缺料", gum.matname)
            pass
        gum.flag = 2
        gum.save()
    # gum_set.update(flag=2)


def sync_cb(db, pb, recipe_name):
    pb.batching_details.all().filter(type=2).update(delete_flag=True)
    cb_set = SfjRecipeCb.objects.using(db).filter(recipe_name=recipe_name, flag=1)
    for gum in cb_set:
        try:
            tank_no = str(int(gum.matcode[3:].strip()))
        except:
            tank_no = None
        if gum.matcode.strip() != "卸料" and gum.matname.strip() != "卸料":
            material = Material.objects.filter(material_name=gum.matcode.strip()).first()
        else:
            material = Material.objects.filter(material_name="卸料", material_type__global_name="炭黑").first()
            tank_no = "卸料"
        try:
            ProductBatchingDetail.objects.create(
                product_batching=pb,
                sn=gum.act_code,
                material=material,
                actual_weight=gum.set_weight,
                standard_error=gum.error_allow,
                auto_flag=1,
                tank_no = tank_no,
                type=2
            )
        except Exception as e:
            print("缺炭黑：", gum.matname)
            logger.error("缺炭黑：", gum.matname)
            pass
        gum.flag = 2
        gum.save()
    # cb_set.update(flag=2)


def sync_oil1(db, pb, recipe_name):
    pb.batching_details.all().filter(type=3).update(delete_flag=True)
    oil1_set = SfjRecipeOil1.objects.using(db).filter(recipe_name=recipe_name, flag=1)
    for gum in oil1_set:
        try:
            tank_no = str(int(gum.matcode[3:].strip()))
        except:
            tank_no = None
        if gum.matcode.strip() != "卸料" and gum.matname.strip() != "卸料":
            material = Material.objects.filter(material_name=gum.matcode.strip()).first()
        else:
            material = Material.objects.filter(material_name="卸料", material_type__global_name="油料").first()
            tank_no = "卸料"
        try:
            ProductBatchingDetail.objects.create(
                product_batching=pb,
                sn=gum.act_code,
                material=material,
                actual_weight=gum.set_weight,
                standard_error=gum.error_allow,
                auto_flag=1,
                tank_no=tank_no,
                type=3
            )
        except Exception as e:
            print("缺油", gum.matname)
            logger.error("缺油", gum.matname)
            pass
        gum.flag = 2
        gum.save()
    # oil1_set.update(flag=2)


def sync_plan(db, pb):
    plan_set = SfjProducePlan.objects.using(db).filter(flag=1)
    equip = Equip.objects.get(equip_no=db)
    # 8-20  20-8
    #  早    夜
    # 1、根据时间和班次判断工厂时间（这一块比较重要，如何根据时间和班次找到他的工厂时间）
    for plan in plan_set:
        actual_times = plan.latesttime
        classes = plan.grouptime
        if classes == "晚班":
            classes = "夜班"
        h = int(actual_times.strftime("%H"))
        times = actual_times.strftime("%Y-%m-%d")
        if classes in ["夜班", "晚班"]:
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
        # 按照三班两运转可以根据班组跟当日排班确定班组
        # wsp_group = GlobalCode.objects.filter(global_name=group).first()
        wsp_obj = WorkSchedulePlan.objects.filter(classes=wsp_classes, plan_schedule=ps_obj).first()
        if not wsp_obj:
            continue
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
        plan.flag = 2
        plan.save()



def sync_recipe(db):
    factory = GlobalCode.objects.get(global_name='安吉')
    recipe_set = SfjRecipeCon.objects.using(db).filter(flag=1)
    equip = Equip.objects.get(equip_no=db)
    for recipe in recipe_set:
        recipe_name = recipe.recipe_name.strip()
        print(recipe_name)
        product_info = recipe_name.split('-')
        if len(product_info) < 2:
            continue
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
                versions=product_info[3].strip()
            )
            # 这边需要确认已存在于群控的配方，在上辅机被修改了怎么处理，按上辅机的来再将状态修改为编辑，需要重新提交，启用
            # 还是直接跳过,暂时先略过
            # pb = pb_set.last()
            # pb.factory = factory
            # pb.site = GlobalCode.objects.get(global_name=product_info[0])
            # pb.product_info = ProductInfo.objects.get_or_create(product_name=product_info[2],
            #                                                     product_no=product_info[2])[0]
            # pb.stage = GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次')
            # pb.dev_type = equip.category
            # pb.versions = product_info[3].strip()
            # pb.used_type = 1
            # pb.save()
            try:
                ProductProcess.objects.get_or_create(
                    product_batching=pb,
                    defaults=dict(
                    equip_code=recipe.equip_code,
                    mini_time=recipe.mini_time,
                    max_time=recipe.max_time,
                    over_time=recipe.max_time,
                    mini_temp=recipe.mini_temp,
                    max_temp=recipe.max_temp,
                    over_temp=recipe.over_temp,
                    reuse_flag=False if int(recipe.if_not) == -1 else True,
                    zz_temp=recipe.rot_temp,
                    xlm_temp=recipe.shut_temp,
                    cb_temp=recipe.side_temp,
                    temp_use_flag=False if int(recipe.temp_on_off) == 1 else True,
                    sp_num=2,
                    reuse_time=recipe.reuse_time)
                )
            except IntegrityError:
                pass
            sync_recipe_mix(db, pb, recipe_name)
            sync_gum(db, pb, recipe_name)
            sync_cb(db, pb, recipe_name)
            sync_oil1(db, pb, recipe_name)
            sync_plan(db, pb)
            recipe.flag = 2
            recipe.save()

@atomic
def sync_product_feedback(db):
    total_equip = SfjEquipStatus.objects.using(db).filter()
    total_equip_set = total_equip.values()
    equip_list = []
    for x in total_equip_set:
        equip_list.append(EquipStatus(
            plan_classes_uid=x.get("plan_classes_uid", "无计划号"),
            equip_no=x.get("equip_no", "Z00"),
            temperature=x.get("temperature",1),
            rpm=x.get("rpm",1),
            energy=x.get("energy",1),
            power=x.get("power",1),
            pressure=x.get("pressure",1),
            status=x.get("status", "运行中"),
            current_trains=x.get("current_trains",1),
            product_time=x.get("product_time")
        ))
    EquipStatus.objects.bulk_create(equip_list)
    total_equip.delete()
    al = AlarmLog.objects.filter(equip_no=db).order_by("product_time").last()
    if al:
        product_time = al.product_time
        sfj_al_set = SfjAlarmLog.objects.using(db).filter(latesttime__gt=product_time).values("content", "latesttime")
        sfj_list = [AlarmLog(equip_no=db, content=x.get("content", ""), product_time=x.get("latesttime")) for x in sfj_al_set]
        AlarmLog.objects.bulk_create(sfj_list)
    else:
        sfj_al_set = SfjAlarmLog.objects.using(db).filter().values("content", "latesttime")
        sfj_list = [AlarmLog(equip_no=db, content=x.get("content", ""), product_time=x.get("latesttime")) for x in
                    sfj_al_set]
        AlarmLog.objects.bulk_create(sfj_list)




if __name__ == '__main__':
    for db in DATABASES:
        if not db.startswith("Z"):
            continue
        else:
            try:
                sync_recipe(db)
            except Exception as e:
                print(e)
                logger.error(e)
            try:
                sync_product_feedback(db)
            except Exception as e:
                print(e)
                logger.error(e)