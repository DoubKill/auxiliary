from django.db import models
from system.models import AbstractEntity
from basics.models import Equip, PlanSchedule, ClassesDetail
from recipe.models import ProductBatching, Material
import uuid
from plan.uuidfield import UUidTools
import time


# Create your models here.
class ProductDayPlan(AbstractEntity):
    """胶料日计划表"""
    equip = models.ForeignKey(Equip, on_delete=models.DO_NOTHING, help_text='机台id', verbose_name='机台id',
                              related_name='equip_product_day_plan')
    product_batching = models.ForeignKey(ProductBatching, on_delete=models.DO_NOTHING, help_text='配料id',
                                         verbose_name='配料id',
                                         related_name='pb_day_plan')
    plan_schedule = models.ForeignKey(PlanSchedule, on_delete=models.DO_NOTHING, help_text='排班计划id',
                                      verbose_name='排班计划id',
                                      related_name='ps_day_plan')

    class Meta:
        # unique_together = (("product_batching", "plan_schedule"),)
        db_table = 'product_day_plan'
        verbose_name_plural = verbose_name = '胶料日计划'


class ProductClassesPlan(AbstractEntity):
    """胶料日班次计划表"""
    product_day_plan = models.ForeignKey(ProductDayPlan, on_delete=models.DO_NOTHING, help_text='胶料日计划id',
                                         verbose_name='胶料日计划id',
                                         related_name='pdp_product_classes_plan')
    sn = models.PositiveIntegerField(verbose_name='顺序', help_text='顺序')
    plan_trains = models.PositiveIntegerField(verbose_name='车次', help_text='车次')
    time = models.DecimalField(verbose_name='消耗时间', help_text='消耗时间',
                                 decimal_places=2, max_digits=8, blank=True, null=True)  # 车次*每一车的时间
    begin_time = models.DateTimeField(verbose_name='开始时间', null=True, blank=True)
    end_time = models.DateTimeField(verbose_name='结束时间', null=True, blank=True)
    weight = models.DecimalField(verbose_name='重量', help_text='重量',
                                 decimal_places=2, max_digits=8, blank=True, null=True)
    unit = models.CharField(max_length=8, help_text='单位', verbose_name='单位')
    classes_detail = models.ForeignKey(ClassesDetail, on_delete=models.DO_NOTHING, help_text='班次id',
                                       verbose_name='班次id',
                                       related_name='cd_product_classes_plan')
    plan_classes_uid = models.UUIDField(verbose_name='班次计划唯一码', help_text='班次计划唯一码',
                                        null=True)

    @property
    def total_time(self):
        return (self.time.hour * 3600 + self.time.minute * 60 + self.time.second) / 60

    class Meta:
        unique_together = (("product_day_plan", "plan_classes_uid"),)
        db_table = 'product_classes_plan'
        verbose_name_plural = verbose_name = '胶料日班次计划'


class ProductBatchingDayPlan(AbstractEntity):
    """配料小料日计划表"""
    equip = models.ForeignKey(Equip, on_delete=models.DO_NOTHING, help_text='机台id', verbose_name='机台id',
                              related_name='equip_product_batching_day_plan')
    product_batching = models.ForeignKey(ProductBatching, on_delete=models.DO_NOTHING, help_text='配料id',
                                         verbose_name='配料id',
                                         related_name='pb_product_batching_day_plan')
    plan_schedule = models.ForeignKey(PlanSchedule, on_delete=models.DO_NOTHING, help_text='排班计划id',
                                      verbose_name='排班计划id',
                                      related_name='ps_product_batching_day_plan')
    bags_total_qty = models.PositiveIntegerField(verbose_name='日计划袋数', help_text='日计划袋数')
    product_day_plan = models.ForeignKey(ProductDayPlan, on_delete=models.DO_NOTHING, help_text='炼胶日计划id',
                                         verbose_name='炼胶日计划id',
                                         related_name='pdp_product_batching_day_plan', null=True, default=None)

    class Meta:
        db_table = 'product_batching_day_plan'
        verbose_name_plural = verbose_name = '配料小料日计划'


class ProductBatchingClassesPlan(AbstractEntity):
    """配料料日班次计划表"""
    product_batching_day_plan = models.ForeignKey(ProductBatchingDayPlan, on_delete=models.DO_NOTHING,
                                                  help_text='配料日计划id',
                                                  verbose_name='配料日计划id',
                                                  related_name='pdp_product_batching_classes_plan')
    sn = models.PositiveIntegerField(verbose_name='顺序', help_text='顺序')
    bags_qty = models.PositiveIntegerField(verbose_name='袋数', help_text='袋数')
    # time = models.TimeField(verbose_name='时间', help_text='时间')
    # weight = models.DecimalField(verbose_name='重量', help_text='重量',
    #                              decimal_places=2, max_digits=8, blank=True, null=True)
    unit = models.CharField(max_length=8, help_text='单位', verbose_name='单位')
    classes_detail = models.ForeignKey(ClassesDetail, on_delete=models.DO_NOTHING, help_text='班次id',
                                       verbose_name='班次id',
                                       related_name='cd_product_batching_classes_plan')
    plan_classes_uid = models.UUIDField(default=uuid.uuid4(), verbose_name='班次计划唯一码', help_text='班次计划唯一码', null=True)

    class Meta:
        db_table = 'product_batching_classes_plan'
        verbose_name_plural = verbose_name = '配料料日班次计划'


class MaterialDemanded(AbstractEntity):
    """原材料需求量表"""
    classes = models.ForeignKey(ClassesDetail, on_delete=models.DO_NOTHING, help_text='班次id',
                                verbose_name='班次id',
                                related_name='c_material_demanded')
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING, help_text='原材料id',
                                 verbose_name='原材料id',
                                 related_name='m_material_demanded')
    material_demanded = models.PositiveIntegerField(verbose_name='原材料需求重量', help_text='原材料需求重量')
    plan_classes_uid = models.CharField(max_length=128, verbose_name='班次计划唯一码', help_text='班次计划唯一码', null=True)
    plan_schedule = models.ForeignKey(PlanSchedule, on_delete=models.DO_NOTHING, help_text='排班计划id',
                                      verbose_name='排班计划id',
                                      related_name='ps_material_demanded')

    class Meta:
        db_table = 'material_demanded'
        verbose_name_plural = verbose_name = '原材料需求量'


class MaterialRequisitionClasses(AbstractEntity):
    """领料日班次计划表"""
    material_demanded = models.ManyToManyField(MaterialDemanded,
                                               help_text='原材料需求量id',
                                               verbose_name='原材料需求量id',
                                               related_name='md_material_requisition_classes')
    # sn = models.PositiveIntegerField(verbose_name='顺序', help_text='顺序',null=True)
    weight = models.DecimalField(verbose_name='重量', help_text='重量',
                                 decimal_places=2, max_digits=8, blank=True, null=True)
    unit = models.CharField(max_length=64, help_text='单位', verbose_name='单位')
    classes_detail = models.ForeignKey(ClassesDetail, on_delete=models.DO_NOTHING, help_text='班次id',
                                       verbose_name='班次id',
                                       related_name='cd_material_requisition_classes', null=True)
    plan_classes_uid = models.UUIDField(default=uuid.uuid4(), verbose_name='班次计划唯一码', help_text='班次计划唯一码', null=True)

    class Meta:
        db_table = 'material_requisition_classes'
        verbose_name_plural = verbose_name = '领料日班次计划'


'''
class MaterialRequisition(AbstractEntity):
    """领料日计划表"""
    material_demanded = models.ForeignKey(MaterialDemanded, on_delete=models.DO_NOTHING, help_text='计划原材料需求量id',
                                          verbose_name='计划原材料需求量id',
                                          related_name='md_material_requisition')
    count = models.PositiveIntegerField(verbose_name='总计', help_text='总计')
    plan_schedule = models.ForeignKey(PlanSchedule, on_delete=models.DO_NOTHING, help_text='排班计划id',
                                      verbose_name='排班计划id',
                                      related_name='ps_material_requisition')
    unit = models.CharField(max_length=8, help_text='单位', verbose_name='单位')

    class Meta:
        db_table = 'material_requisition'
        verbose_name_plural = verbose_name = '领料日计划'
'''

'''
class MaterialStorage(AbstractEntity):
    """物料库存表"""
    material = models.ForeignKey(Material, on_delete=models.DO_NOTHING, help_text='物料id',
                                 verbose_name='物料id',
                                 related_name='m_material_storage')
    qty = models.PositiveIntegerField(help_text='库存数量', verbose_name='库存数量')
    qty_unit = models.CharField(max_length=8, help_text='数量单位', verbose_name='数量单位')
    weight = models.DecimalField(verbose_name='库存重量', help_text='库存重量',
                                 decimal_places=2, max_digits=8, blank=True, null=True)

    weight_unit = models.CharField(max_length=8, help_text='重量单位', verbose_name='重量单位')

    class Meta:
        db_table = 'material_storage'
        verbose_name_plural = verbose_name = '物料库存表'
'''
