# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/9/29
name: 
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from plan.models import ProductDayPlan
from system.models import DataSynchronization


@receiver(post_save, sender=ProductDayPlan)
def plan_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    if not created:
        """更新了数据则需要从同步表中删除此记录"""
        DataSynchronization.objects.filter(type=11, obj_id=instance.id).delete()
