# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/10/27
name: 
"""
import os

import django
from django.db.models import Count
from django.db.models.functions import Extract, ExtractMonth

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from production.models import *

ff = PlanStatus.objects.all().annotate(month=ExtractMonth("product_time")).values("month", "status").annotate(count=Count("id"))
print(ff)