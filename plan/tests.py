# Create your tests here.
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from work_station import models as md
from production.models import PlanStatus

# 与收皮机对接测试
i = 1
model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownRecipePloy', 'IfdownRecipeOil1',
              'IfdownRecipeCb', 'IfdownPmtRecipe', "IfdownRecipeWeigh"]
for model_obj in model_list:
    model_name = getattr(md, model_obj + str(i))
    model_name.objects.all().update(recstatus='运行中')
    PlanStatus.objects.filter(id=2).update(status='运行中')
    # model_name.objects.all().update(recstatus='等待')
    # model_name.objects.all().delete()
    # PlanStatus.objects.filter(id=2).update(status='等待')
