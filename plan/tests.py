# Create your tests here.
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from plan.models import ProductClassesPlan

from work_station import models as md
from production.models import PlanStatus

# 与收皮机对接测试

# pcp_obj = ProductClassesPlan.objects.filter(id=1).first()
# pcp_obj.plan_trains = 123
# pcp_obj.save()
# i = 6
# model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownRecipePloy', 'IfdownRecipeOil1',
#               'IfdownRecipeCb', 'IfdownPmtRecipe', "IfdownRecipeWeigh"]
# for model_obj in model_list:
#     model_name = getattr(md, model_obj + str(i))
#     model_name.objects.all().update(recstatus='运行中')
#     PlanStatus.objects.filter(id=7).update(status='运行中')
#     model_name.objects.all().update(recstatus='等待')
#     model_name.objects.all().delete()
#     PlanStatus.objects.filter().update(status='等待')


# pcp_set = ProductClassesPlan.objects.all()
# for pcp_obj in pcp_set:
#     uid = pcp_obj.plan_classes_uid
#     new_pcp = ProductClassesPlan.objects.using('mes').filter(plan_classes_uid=uid)
#     print(pcp_obj.plan_trains, new_pcp.first().plan_trains)
#     print('---------------------------------------------------')
#     # new_pcp.update(plan_trains=pcp_obj.plan_trains)
