
from django.db import models
from basics.models import GlobalCode, Equip, EquipCategoryAttribute
from system.models import AbstractEntity, User


class Material(AbstractEntity):
    """原材料信息"""
    material_no = models.CharField(max_length=64, help_text='原材料编码', verbose_name='原材料编码', unique=True)
    material_name = models.CharField(max_length=64, help_text='原材料名称', verbose_name='原材料名称')
    for_short = models.CharField(max_length=64, help_text='原材料简称', verbose_name='原材料简称', blank=True, null=True)
    material_type = models.ForeignKey(GlobalCode, help_text='原材料类别', verbose_name='原材料类别',
                                      on_delete=models.DO_NOTHING, related_name='mt_materials')
    package_unit = models.ForeignKey(GlobalCode, help_text='包装单位', verbose_name='包装单位',
                                     on_delete=models.DO_NOTHING, related_name='pu_materials', blank=True, null=True)
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    def __str__(self):
        return self.material_name

    class Meta:
        db_table = 'material'
        verbose_name_plural = verbose_name = '原材料'


class MaterialAttribute(AbstractEntity):
    """原材料属性"""
    material = models.OneToOneField(Material, help_text='原材料', verbose_name='原材料',
                                    on_delete=models.CASCADE, related_name='material_attr')
    safety_inventory = models.PositiveIntegerField(help_text='安全库存标准', verbose_name='安全库存标准')
    period_of_validity = models.PositiveIntegerField(help_text='有效期', verbose_name='有效期')
    validity_unit = models.CharField('有效期单位', help_text='有效期单位', max_length=8, default="天")

    class Meta:
        db_table = 'material_attribute'
        verbose_name_plural = verbose_name = '原材料属性'


class MaterialSupplier(AbstractEntity):
    """原材料产地"""
    material = models.ForeignKey(Material, help_text='原材料', verbose_name='原材料', on_delete=models.CASCADE)
    supplier_no = models.CharField(max_length=64, help_text='产地编码', verbose_name='编码', unique=True)
    provenance = models.CharField(max_length=64, help_text='产地', verbose_name='产地')
    use_flag = models.BooleanField(help_text='是否启用', verbose_name='是否启用', default=True)

    class Meta:
        db_table = 'material_supplier'
        verbose_name_plural = verbose_name = '原材料产地'


class ProductInfo(AbstractEntity):
    """胶料工艺信息"""
    product_no = models.CharField(max_length=64, help_text='胶料编码', verbose_name='胶料编码', unique=True)
    product_name = models.CharField(max_length=64, help_text='胶料名称', verbose_name='胶料名称')

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'product_info'
        verbose_name_plural = verbose_name = '胶料代码'


class ProductRecipe(AbstractEntity):
    """胶料段次配方标准"""
    product_recipe_no = models.CharField(max_length=64, help_text='胶料标准编号', verbose_name='胶料标准编号')
    sn = models.PositiveIntegerField(verbose_name='序号', help_text='序号')
    product_info = models.ForeignKey(ProductInfo, verbose_name='胶料工艺', help_text='胶料工艺',
                                     on_delete=models.DO_NOTHING)
    material = models.ForeignKey(Material, verbose_name='原材料', help_text='原材料',
                                 on_delete=models.DO_NOTHING, blank=True, null=True)
    stage = models.ForeignKey(GlobalCode, help_text='段次', verbose_name='段次',
                              on_delete=models.DO_NOTHING)
    ratio = models.DecimalField(verbose_name='配比', help_text='配比',
                                decimal_places=2, max_digits=8, blank=True, null=True)

    def __str__(self):
        return self.product_recipe_no

    class Meta:
        db_table = 'product_recipe'
        verbose_name_plural = verbose_name = '胶料段次配方标准'


class ProductBatching(AbstractEntity):
    """胶料配料标准"""
    USE_TYPE_CHOICE = (
        (1, '编辑'),
        (2, '提交'),
        (4, '启用'),
        (5, '驳回'),
        (6, '废弃'),
        (7, '停用')
    )
    BATCHING_TYPE_CHOICE = (
        (1, '机台'),
        (2, '机型')
    )
    factory = models.ForeignKey(GlobalCode, help_text='工厂', verbose_name='工厂',
                                on_delete=models.DO_NOTHING, related_name='f_batching', blank=True, null=True)
    site = models.ForeignKey(GlobalCode, help_text='SITE', verbose_name='SITE',
                             on_delete=models.DO_NOTHING, related_name='s_batching', blank=True, null=True)
    product_info = models.ForeignKey(ProductInfo, help_text='胶料工艺信息',
                                     on_delete=models.DO_NOTHING, blank=True, null=True)
    precept = models.CharField(max_length=64, help_text='方案', verbose_name='方案', blank=True, null=True)
    stage_product_batch_no = models.CharField(max_length=63, help_text='胶料配方编码')
    dev_type = models.ForeignKey(EquipCategoryAttribute, help_text='机型', on_delete=models.DO_NOTHING, blank=True,
                                 null=True)
    stage = models.ForeignKey(GlobalCode, help_text='段次', verbose_name='段次',
                              on_delete=models.DO_NOTHING, related_name='stage_batches', blank=True, null=True)
    versions = models.CharField(max_length=64, help_text='版本', verbose_name='版本', blank=True, null=True)
    used_type = models.PositiveSmallIntegerField(help_text='使用状态', choices=USE_TYPE_CHOICE, default=1)
    batching_weight = models.DecimalField(verbose_name='配料重量', help_text='配料重量',
                                          decimal_places=2, max_digits=8, default=0)
    manual_material_weight = models.DecimalField(verbose_name='手动小料重量', help_text='手动小料重量',
                                                 decimal_places=2, max_digits=8, default=0)
    auto_material_weight = models.DecimalField(verbose_name='自动小料重量', help_text='自动小料重量',
                                               decimal_places=2, max_digits=8, default=0)
    volume = models.DecimalField(verbose_name='配料体积', help_text='配料体积', decimal_places=2, max_digits=8,
                                 blank=True, null=True)
    submit_user = models.ForeignKey(User, help_text='提交人', blank=True, null=True,
                                    on_delete=models.DO_NOTHING, related_name='submit_batching')
    submit_time = models.DateTimeField(help_text='提交时间', blank=True, null=True)
    reject_user = models.ForeignKey(User, help_text='驳回人', blank=True, null=True,
                                    on_delete=models.DO_NOTHING, related_name='reject_batching')
    reject_time = models.DateTimeField(help_text='驳回时间', blank=True, null=True)
    used_user = models.ForeignKey(User, help_text='启用人', blank=True, null=True,
                                  on_delete=models.DO_NOTHING, related_name='used_batching')
    used_time = models.DateTimeField(help_text='启用时间', verbose_name='启用时间', blank=True, null=True)
    obsolete_user = models.ForeignKey(User, help_text='弃用人', blank=True, null=True,
                                      on_delete=models.DO_NOTHING, related_name='obsolete_batching')
    obsolete_time = models.DateTimeField(help_text='弃用时间', verbose_name='弃用时间', blank=True, null=True)
    production_time_interval = models.DecimalField(help_text='炼胶时间(分)', blank=True, null=True,
                                                   decimal_places=2, max_digits=8)
    equip = models.ForeignKey(Equip, help_text='设备', blank=True, null=True, on_delete=models.DO_NOTHING)
    batching_type = models.PositiveIntegerField(verbose_name='配料类型', help_text='配料类型',
                                                choices=BATCHING_TYPE_CHOICE, default=1)
    is_synced = models.BooleanField(default=False, help_text='是否已同步至MES')

    def __str__(self):
        return self.stage_product_batch_no

    class Meta:
        db_table = 'product_batching'
        verbose_name_plural = verbose_name = '胶料配料标准'
        permissions = (
            ('submit_prod', '提交配方'),
            ('using_prod', '启用配方'),
            ('refuse_prod', '驳回配方'),
            ('abandon_prod', '弃用配方')
        )


class ProductBatchingDetail(AbstractEntity):
    AUTO_FLAG = (
        (0, None),
        (1, '自动'),
        (2, '手动'),
    )
    TYPE_CHOICE = (
        (1, '胶料'),
        (2, '炭黑'),
        (3, '油料')
    )
    product_batching = models.ForeignKey(ProductBatching, help_text='配料标准', on_delete=models.DO_NOTHING,
                                         related_name='batching_details')
    sn = models.PositiveIntegerField(verbose_name='序号', help_text='序号')
    material = models.ForeignKey(Material, verbose_name='原材料', help_text='原材料', on_delete=models.DO_NOTHING)
    actual_weight = models.DecimalField(verbose_name='重量', help_text='重量', decimal_places=3, max_digits=8)
    standard_error = models.DecimalField(help_text='误差值范围', decimal_places=2, max_digits=8, default=0)
    auto_flag = models.PositiveSmallIntegerField(help_text='手动/自动', choices=AUTO_FLAG)
    type = models.PositiveSmallIntegerField(help_text='类别', choices=TYPE_CHOICE, default=1)
    tank_no = models.CharField(max_length=64, help_text='罐号', blank=True, null=True)

    class Meta:
        db_table = 'product_batching_detail'
        verbose_name_plural = verbose_name = '胶料配料标准详情'


class ProductProcess(AbstractEntity):
    """胶料配方步序"""
    product_batching = models.OneToOneField(ProductBatching, help_text='配料标准',
                                            on_delete=models.DO_NOTHING, related_name='processes')
    equip_code = models.PositiveIntegerField(help_text='锁定/解除', default=0)
    reuse_time = models.PositiveIntegerField(help_text='回收时间', default=0)
    mini_time = models.PositiveIntegerField(help_text='超温最短时间', default=0)
    max_time = models.PositiveIntegerField(help_text='超温最长时间', default=0)  # 该字段并未实际使用
    mini_temp = models.PositiveIntegerField(help_text='进胶最低温度', default=0)
    max_temp = models.PositiveIntegerField(help_text='进胶最高温度', default=0)
    over_time = models.PositiveIntegerField(help_text='炼胶超时时间', default=0)
    over_temp = models.PositiveIntegerField(help_text='超温温度', default=0)
    reuse_flag = models.BooleanField(help_text='是否回收，（true:回收,false:不回收）', default=False)
    zz_temp = models.PositiveIntegerField(help_text='转子水温', default=0)
    xlm_temp = models.PositiveIntegerField(help_text='卸料门水温', default=0)
    cb_temp = models.PositiveIntegerField(help_text='侧壁水温', default=0)
    temp_use_flag = models.BooleanField(help_text='三区水温启用/停用，（true:启用,false:停用）', default=True)
    use_flag = models.BooleanField(help_text='配方启用/弃用，（true:启用,false:弃用）', default=True)
    batching_error = models.PositiveIntegerField(help_text='胶料总误差', default=0)
    sp_num = models.DecimalField(help_text='收皮', default=0, decimal_places=1, max_digits=3)

    class Meta:
        db_table = 'product_process'
        verbose_name_plural = verbose_name = '胶料配料标准步序'


class BaseCondition(AbstractEntity):
    code = models.CharField(max_length=16, help_text='代码')
    condition = models.CharField(max_length=16, help_text='条件名称')

    class Meta:
        db_table = 'base_condition'
        verbose_name_plural = verbose_name = '基本条件'


class BaseAction(AbstractEntity):
    code = models.CharField(max_length=16, help_text='代码')
    action = models.CharField(max_length=16, help_text='条件名称')

    class Meta:
        db_table = 'base_action'
        verbose_name_plural = verbose_name = '基本动作'


class ProductProcessDetail(AbstractEntity):
    product_batching = models.ForeignKey(ProductBatching, help_text='配方id', on_delete=models.DO_NOTHING,
                                         related_name='process_details')
    sn = models.PositiveIntegerField(help_text='序号')
    temperature = models.PositiveIntegerField(help_text='温度', default=0)
    rpm = models.DecimalField(help_text='转速', default=0, decimal_places=1, max_digits=8)
    energy = models.DecimalField(help_text='能量', default=0, decimal_places=1, max_digits=8)
    power = models.DecimalField(help_text='功率', default=0, decimal_places=1, max_digits=8)
    pressure = models.DecimalField(help_text='压力', default=0, decimal_places=1, max_digits=8)
    condition = models.ForeignKey(BaseCondition, help_text='条件id', blank=True, null=True, on_delete=models.DO_NOTHING)
    time = models.PositiveIntegerField(help_text='时间(分钟)', default=0)
    action = models.ForeignKey(BaseAction, help_text='基本动作id', blank=True, null=True, on_delete=models.DO_NOTHING)
    time_unit = models.CharField(max_length=4, help_text='时间单位', default='秒')

    class Meta:
        db_table = 'product_process_detail'
        verbose_name_plural = verbose_name = '胶料配料标准步序详情'


class RecipeUpdateHistory(AbstractEntity):
    product_no = models.CharField(max_length=64, help_text='胶料配方编码')
    equip_no = models.CharField(max_length=64, help_text='机台号')
    recipe_detail = models.TextField(max_length=1024, help_text='整个机台配方详情')
    username = models.CharField(max_length=16, help_text='用户名称')

    class Meta:
        db_table = 'recipe_update_history'
        verbose_name_plural = verbose_name = '配方详情历史记录'