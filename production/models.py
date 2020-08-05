from django.db import models

from basics.models import AbstractEntity

class TrainsFeedbacks(AbstractEntity):
    """车次/批次产出反馈"""
    plan_classes_uid = models.UUIDField(help_text='班次计划唯一码', verbose_name='班次计划唯一码')
    plan_trains = models.IntegerField(help_text='计划车次', verbose_name='计划车次')
    actual_trains = models.IntegerField(help_text='实际车次', verbose_name='实际车次')
    bath_no = models.IntegerField(help_text='批次', verbose_name='批次')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际重量', verbose_name='实际重量')
    begin_time = models.DateTimeField(help_text='开始时间', verbose_name='开始时间')
    end_time = models.DateTimeField(help_text='结束时间', verbose_name='结束时间')
    operation_user = models.CharField(max_length=74, help_text='操作员', verbose_name='操作员')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.bath_no}|{self.equip_no}"

    class Meta:
        db_table = 'trains_feedbacks'
        verbose_name_plural = verbose_name = '胶料车次产出反馈'


class PalletFeedbacks(AbstractEntity):
    """托盘产出反馈"""
    plan_classes_uid = models.UUIDField(help_text='班次计划唯一码', verbose_name='班次计划唯一码')
    bath_no = models.IntegerField(help_text='批次', verbose_name='批次')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际重量', verbose_name='实际重量')
    begin_time = models.DateTimeField(help_text='开始时间', verbose_name='开始时间')
    end_time = models.DateTimeField(help_text='结束时间', verbose_name='结束时间')
    operation_user = models.CharField(max_length=74, help_text='操作员', verbose_name='操作员')
    begin_trains = models.IntegerField(help_text='开始车次', verbose_name='开始车次')
    end_trains = models.IntegerField(help_text='结束车次', verbose_name='结束车次')
    pallet_no = models.CharField(max_length=64, help_text='托盘', verbose_name='托盘')
    barcode = models.CharField(max_length=64, help_text='收皮条码', verbose_name='收皮条码')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.barcode}|{self.equip_no}"

    class Meta:
        db_table = 'pallet_feedbacks'
        verbose_name_plural = verbose_name = '胶料托盘产出反馈'


class EquipStatus(AbstractEntity):
    """机台状况反馈"""
    plan_classes_uid = models.UUIDField(help_text='班次计划唯一码', verbose_name='班次计划唯一码')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    temperature = models.DecimalField(decimal_places=2, max_digits=8, help_text='温度', verbose_name='温度')
    rpm = models.DecimalField(decimal_places=2, max_digits=8, help_text='转速', verbose_name='转速')
    energy = models.DecimalField(decimal_places=2, max_digits=8, help_text='能量', verbose_name='能量')
    power = models.DecimalField(decimal_places=2, max_digits=8, help_text='功率', verbose_name='功率')
    pressure = models.DecimalField(decimal_places=2, max_digits=8, help_text='压力', verbose_name='压力')
    status = models.CharField(max_length=64, help_text='状态', verbose_name='状态')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}"

    class Meta:
        db_table = 'equip_status'
        verbose_name_plural = verbose_name = '机台状况反馈'


class PlanStatus(AbstractEntity):
    """计划状态变更"""
    plan_classes_uid = models.UUIDField(help_text='班次计划唯一码', verbose_name='班次计划唯一码')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    status = models.CharField(max_length=64, help_text='状态', verbose_name='状态')
    operation_user = models.CharField(max_length=74, help_text='操作员', verbose_name='操作员')
    energy = models.DecimalField(decimal_places=2, max_digits=8, help_text='能量', verbose_name='能量')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}|{self.product_no}"

    class Meta:
        db_table = 'plan_status'
        verbose_name_plural = verbose_name = '计划状态变更'


class ExpendMaterial(AbstractEntity):
    """原材料消耗表"""
    plan_classes_uid = models.UUIDField(help_text='班次计划唯一码', verbose_name='班次计划唯一码')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    trains = models.IntegerField(help_text='车次', verbose_name='车次')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际消耗重量', verbose_name='实际消耗重量')
    masterial_no = models.CharField(max_length=64, help_text='原材料id', verbose_name='原材料id')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}|{self.product_no}|{self.masterial_no}"

    class Meta:
        db_table = 'expend_material'
        verbose_name_plural = verbose_name = '原材料消耗'


class OperationLog(AbstractEntity):
    """操作日志"""
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    content = models.CharField(max_length=1024, help_text='操作日志内容', verbose_name='操作日志内容')

    def __str__(self):
        return self.equip_no

    class Meta:
        db_table = 'operation_log'
        verbose_name_plural = verbose_name = '操作日志'


class QualityControl(AbstractEntity):
    """质检结果表"""
    barcode = models.CharField(max_length=64, help_text='收皮条码', verbose_name='收皮条码')
    qu_content = models.CharField(max_length=1024, help_text='质检内容', verbose_name='质检内容')

    def __str__(self):
        return self.barcode

    class Meta:
        db_table = 'quality-control'
        verbose_name_plural = verbose_name = '质检结果'
