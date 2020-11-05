# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/11/5
name: 
"""
import os

import django
from django.db.models import Count, Sum
from django.db.models.functions import Extract, ExtractMonth

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from recipe.models import *

for equip_id in range(1,16):
    pb_set = ProductBatching.objects.filter(equip_id=equip_id)
    for pb in pb_set:
        temp = pb.batching_details.all().filter(delete_flag=False).aggregate(weight=Sum("actual_weight"))
        if temp:
            weight = temp.get("weight")
            if weight:
                pb.batching_weight = weight
                pb.save()