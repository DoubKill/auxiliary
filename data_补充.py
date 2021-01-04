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

from production.models import TrainsFeedbacks, IfupReportBasisBackups

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()


def run():
    trains_set = TrainsFeedbacks.objects.filter(equip_no="Z06")
    for trains in trains_set:
        uid = trains.plan_classes_uid
        actual_trains = trains.actual_trains
        product_no = trains.product_no
        temp = IfupReportBasisBackups.objects.filter(车次号=actual_trains, 计划号=uid, 配方号=product_no).last()
        trains.control_mode = temp.控制方式
        trains.operating_type = models.CharField(max_length=8, blank=True, null=True, help_text='作业方式', verbose_name='作业方式')
        trains.evacuation_time = models.IntegerField(blank=True, null=True, help_text='排胶时间', verbose_name='排胶时间')
        trains.evacuation_temperature = models.IntegerField(blank=True, null=True, help_text='排胶温度', verbose_name='排胶温度')
        trains.evacuation_energy = models.IntegerField(blank=True, null=True, help_text='排胶能量', verbose_name='排胶能量')
        trains.interval_time = models.IntegerField(blank=True, null=True, help_text='间隔时间', verbose_name='间隔时间')
        trains.mixer_time = models.IntegerField(blank=True, null=True, help_text='密炼时间', verbose_name='密炼时间')

        trains.evacuation_power = models.CharField(max_length=64, blank=True, null=True, help_text='排胶功率', verbose_name='排胶功率')
        trains.consum_time = models.IntegerField(blank=True, null=True, help_text='消耗总时间', verbose_name='消耗总时间')
        trains.gum_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='胶料重量', verbose_name='胶料重量',
                                         null=True,
                                         blank=True)
        trains.cb_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='炭黑重量', verbose_name='炭黑重量',
                                        null=True,
                                        blank=True)
        trains.oil1_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='油1重量', verbose_name='油1重量',
                                          null=True,
                                          blank=True)
        trains.oil2_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='油2重量', verbose_name='油2重量',
                                          null=True,
                                          blank=True)
        trains.add_gum_time = models.IntegerField(blank=True, null=True, help_text='加胶时间', verbose_name='加胶时间')
        trains.add_cb_time = models.IntegerField(blank=True, null=True, help_text='加炭黑时间', verbose_name='加炭黑时间')
        trains.add_oil1_time = models.IntegerField(blank=True, null=True, help_text='加油1时间', verbose_name='加油1时间')
        trains.add_oil2_time = models.IntegerField(blank=True, null=True, help_text='加油1时间', verbose_name='加油1时间')


if __name__ == '__main__':
    pass