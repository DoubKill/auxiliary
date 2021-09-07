from django.db import models

from basics.models import AbstractEntity


class TrainsFeedbacks(AbstractEntity):
    """车次产出反馈"""
    # id = models.BigIntegerField(primary_key=True, auto_created=True, unique=True)
    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=64)
    plan_trains = models.IntegerField(help_text='计划车次', verbose_name='计划车次')
    actual_trains = models.IntegerField(help_text='实际车次', verbose_name='实际车次')
    bath_no = models.IntegerField(help_text='批次', verbose_name='批次')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际重量', verbose_name='实际重量')
    begin_time = models.DateTimeField(help_text='开始时间', verbose_name='开始时间')
    end_time = models.DateTimeField(help_text='结束时间', verbose_name='结束时间')
    operation_user = models.CharField(max_length=64, help_text='操作员', verbose_name='操作员')
    classes = models.CharField(max_length=64, help_text='班次', verbose_name='班次')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)

    '''中间表字段补充'''
    control_mode = models.CharField(max_length=8, blank=True, null=True, help_text='控制方式', verbose_name='控制方式')
    operating_type = models.CharField(max_length=8, blank=True, null=True, help_text='作业方式', verbose_name='作业方式')
    evacuation_time = models.IntegerField(blank=True, null=True, help_text='排胶时间', verbose_name='排胶时间')
    evacuation_temperature = models.IntegerField(blank=True, null=True, help_text='排胶温度', verbose_name='排胶温度')
    evacuation_energy = models.IntegerField(blank=True, null=True, help_text='排胶能量', verbose_name='排胶能量')
    interval_time = models.IntegerField(blank=True, null=True, help_text='间隔时间', verbose_name='间隔时间')
    mixer_time = models.IntegerField(blank=True, null=True, help_text='密炼时间', verbose_name='密炼时间')

    evacuation_power = models.CharField(max_length=64, blank=True, null=True, help_text='排胶功率', verbose_name='排胶功率')
    consum_time = models.IntegerField(blank=True, null=True, help_text='消耗总时间', verbose_name='消耗总时间')
    gum_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='胶料重量', verbose_name='胶料重量', null=True,
                                     blank=True)
    cb_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='炭黑重量', verbose_name='炭黑重量', null=True,
                                    blank=True)
    oil1_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='油1重量', verbose_name='油1重量', null=True,
                                      blank=True)
    oil2_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='油2重量', verbose_name='油2重量', null=True,
                                      blank=True)
    add_gum_time = models.IntegerField(blank=True, null=True, help_text='加胶时间', verbose_name='加胶时间')
    add_cb_time = models.IntegerField(blank=True, null=True, help_text='加炭黑时间', verbose_name='加炭黑时间')
    add_oil1_time = models.IntegerField(blank=True, null=True, help_text='加油1时间', verbose_name='加油1时间')
    add_oil2_time = models.IntegerField(blank=True, null=True, help_text='加油1时间', verbose_name='加油1时间')

    @property
    def time(self):
        temp = self.end_time - self.begin_time
        return temp.total_seconds()

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.bath_no}|{self.equip_no}"

    class Meta:
        db_table = 'trains_feedbacks'
        verbose_name_plural = verbose_name = '胶料车次产出反馈'
        indexes = [
            models.Index(fields=['plan_classes_uid']),
            models.Index(fields=['equip_no']),
            models.Index(fields=['product_no']),
            models.Index(fields=['operation_user']),
            models.Index(fields=['begin_time']),
            models.Index(fields=['end_time']), ]


class PalletFeedbacks(AbstractEntity):
    """托盘产出反馈"""
    # id = models.BigIntegerField(primary_key=True, auto_created=True, unique=True)
    plan_classes_uid = models.CharField(help_text='班次计划唯一码/计划编号', verbose_name='班次计划唯一码', max_length=64)
    bath_no = models.IntegerField(help_text='批次', verbose_name='批次')
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际重量', verbose_name='实际重量')
    begin_time = models.DateTimeField(help_text='开始时间', verbose_name='开始时间', auto_created=True)  # 根据结束时间大概往前提几分钟
    end_time = models.DateTimeField(help_text='结束时间', verbose_name='结束时间')
    operation_user = models.CharField(max_length=74, help_text='操作员', verbose_name='操作员')
    begin_trains = models.IntegerField(help_text='开始车次', verbose_name='开始车次')
    end_trains = models.IntegerField(help_text='结束车次', verbose_name='结束车次')
    pallet_no = models.CharField(max_length=64, help_text='托盘', verbose_name='托盘')
    classes = models.CharField(max_length=64, help_text='班次', verbose_name='班次')
    lot_no = models.CharField(max_length=64, help_text='追踪号/收皮条码', verbose_name='追踪号/收皮条码')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.lot_no}|{self.equip_no}"

    class Meta:
        db_table = 'pallet_feedbacks'
        verbose_name_plural = verbose_name = '胶料托盘产出反馈'
        indexes = [
            models.Index(fields=['plan_classes_uid']),
            models.Index(fields=['equip_no']),
            models.Index(fields=['product_no']),
            models.Index(fields=["classes"]),
            models.Index(fields=["pallet_no"]),
            models.Index(fields=["end_time"]), ]


class EquipStatus(AbstractEntity):
    """机台状况反馈"""
    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=64)
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    temperature = models.DecimalField(decimal_places=2, max_digits=8, help_text='温度', verbose_name='温度')
    rpm = models.DecimalField(decimal_places=2, max_digits=8, help_text='转速', verbose_name='转速')
    energy = models.DecimalField(decimal_places=2, max_digits=8, help_text='能量', verbose_name='能量')
    power = models.DecimalField(decimal_places=2, max_digits=8, help_text='功率', verbose_name='功率')
    pressure = models.DecimalField(decimal_places=2, max_digits=8, help_text='压力', verbose_name='压力')
    status = models.CharField(max_length=64, help_text='状态：运行中、等待、故障', verbose_name='状态',
                              choices=(('运行中', '运行中'), ('等待', '等待'), ('故障', '故障')), default="运行中")
    current_trains = models.IntegerField(help_text='当前车次', verbose_name='当前车次')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}"

    class Meta:
        db_table = 'equip_status'
        verbose_name_plural = verbose_name = '机台状况反馈'
        indexes = [
            models.Index(fields=['equip_no']),
            models.Index(fields=['plan_classes_uid']),
            models.Index(fields=['product_time']),
            models.Index(fields=['current_trains']), ]


class PlanStatus(AbstractEntity):
    """计划状态变更"""

    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=64)
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    status = models.CharField(max_length=64, help_text='状态:等待、已下达、运行中、完成', verbose_name='状态',
                              choices=(('等待', '等待'), ('已下达', '已下达'), ('运行中', '运行中'), ('完成', '完成'), ('待停止', '待停止')))
    operation_user = models.CharField(max_length=64, help_text='操作员', verbose_name='操作员')
    actual_trains = models.IntegerField(blank=True, null=True, help_text='实际车次', verbose_name='实际车次')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}|{self.product_no}"

    class Meta:
        db_table = 'plan_status'
        verbose_name_plural = verbose_name = '计划状态变更'
        indexes = [
            models.Index(fields=['equip_no']),
            models.Index(fields=['plan_classes_uid']),
            models.Index(fields=['product_no']), ]


class ExpendMaterial(AbstractEntity):
    """原材料消耗表"""
    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=64)
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    trains = models.IntegerField(help_text='车次', verbose_name='车次')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', verbose_name='计划重量')
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际消耗重量', verbose_name='实际消耗重量')
    material_no = models.CharField(max_length=64, help_text='原材料id', verbose_name='原材料id')
    material_type = models.CharField(max_length=64, help_text='原材料类型', verbose_name='原材料类型')
    material_name = models.CharField(max_length=64, help_text='原材料名称', verbose_name='原材料名称')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)
    state_balance = models.CharField(max_length=64, help_text='秤状态', verbose_name='秤状态', null=True)

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}|{self.product_no}|{self.material_no}"

    class Meta:
        db_table = 'expend_material'
        verbose_name_plural = verbose_name = '原材料消耗'
        indexes = [
            models.Index(fields=['equip_no']),
            models.Index(fields=['product_no']),
            models.Index(fields=['material_type']),
            models.Index(fields=['product_time']), ]


class ProcessFeedback(AbstractEntity):
    """步序反馈表"""
    sn = models.PositiveIntegerField(help_text='序号/步骤号')
    condition = models.CharField(max_length=20, help_text='条件', blank=True, null=True)
    time = models.PositiveIntegerField(help_text='时间(秒)', default=0)
    temperature = models.PositiveIntegerField(help_text='温度', default=0)
    power = models.DecimalField(help_text='功率', default=0, decimal_places=1, max_digits=5)
    energy = models.DecimalField(help_text='能量', default=0, decimal_places=1, max_digits=5)
    action = models.CharField(max_length=20, help_text='基本动作', blank=True, null=True)
    rpm = models.PositiveIntegerField(help_text='转速', default=0)
    pressure = models.DecimalField(help_text='压力', default=0, decimal_places=1, max_digits=5)
    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=64)
    product_no = models.CharField(max_length=64, help_text='产出胶料', verbose_name='产出胶料')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    current_trains = models.PositiveIntegerField(help_text='当前车次')

    def __str__(self):
        return f"{self.plan_classes_uid}|{self.equip_no}|{self.product_no}"

    class Meta:
        db_table = 'process_feedback'
        verbose_name_plural = verbose_name = '步序反馈报表'


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


class MaterialTankStatus(AbstractEntity):
    """储料罐状态"""
    TYPE_CHOICE = (
        ('1', '炭黑'),
        ('2', '油料')
    )
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    tank_type = models.CharField(max_length=64, help_text="储料罐类型", verbose_name='储料罐类型', choices=TYPE_CHOICE)
    tank_name = models.CharField(max_length=64, help_text="储料罐名称", verbose_name='储料罐名称')
    tank_no = models.CharField(max_length=64, help_text="储料罐编号", verbose_name='储料罐编号')
    material_no = models.CharField(max_length=64, help_text='原材料id', verbose_name='原材料id')
    material_type = models.CharField(max_length=64, help_text='原材料类型', verbose_name='原材料类型')
    material_name = models.CharField(max_length=64, help_text='原材料名称', verbose_name='原材料名称')
    use_flag = models.BooleanField(help_text="是否启用", verbose_name='是否启用', default=0)
    low_value = models.DecimalField(decimal_places=2, max_digits=8, help_text='慢称值', verbose_name='慢称值')
    advance_value = models.DecimalField(decimal_places=2, max_digits=8, help_text='提前量', verbose_name='提前量')
    adjust_value = models.DecimalField(decimal_places=2, max_digits=8, help_text='调整值', verbose_name='调整值')
    dot_time = models.DecimalField(decimal_places=2, max_digits=8, help_text='点动时间', verbose_name='电动时间')
    fast_speed = models.DecimalField(decimal_places=2, max_digits=8, help_text='快称速度', verbose_name='快称速度')
    low_speed = models.DecimalField(decimal_places=2, max_digits=8, help_text='慢称速度', verbose_name='慢称速度')
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)
    provenance = models.CharField(max_length=64, help_text='产地', verbose_name='产地', blank=True, null=True)

    def __str__(self):
        return f"{self.tank_name}|{self.tank_type}|{self.equip_no}"

    class Meta:
        db_table = 'material_tank_status'
        verbose_name_plural = verbose_name = '储料罐状态'
        indexes = [models.Index(fields=['equip_no']), ]


'''为了车次报表 将中间表的部分表复制过来 相当于备份表 因为中间表的数据会定期删除'''


class IfupReportWeightBackups(models.Model):
    """车次报表材料重量表"""
    序号 = models.AutoField(primary_key=True)
    车次号 = models.IntegerField(blank=True, null=True)
    物料名称 = models.CharField(max_length=19, blank=True, null=True)
    设定重量 = models.IntegerField(blank=True, null=True)
    实际重量 = models.IntegerField(blank=True, null=True)
    秤状态 = models.CharField(max_length=8, blank=True, null=True)
    计划号 = models.CharField(max_length=50)
    配方号 = models.CharField(max_length=50)
    物料编码 = models.CharField(max_length=19, blank=True, null=True)
    物料类型 = models.CharField(max_length=1, blank=True, null=True)
    存盘时间 = models.CharField(max_length=19, blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.CharField(db_column='RecStatus', max_length=20)

    class Meta:
        # managed = False
        db_table = 'ifup_report_weight_backups'


class IfupReportBasisBackups(models.Model):
    """车次报表主信息"""
    序号 = models.BigAutoField(primary_key=True)
    车次号 = models.IntegerField(blank=True, null=True)
    开始时间 = models.CharField(max_length=20, blank=True, null=True)
    消耗时间 = models.IntegerField(blank=True, null=True)
    排胶时间 = models.IntegerField(blank=True, null=True)
    间隔时间 = models.IntegerField(blank=True, null=True)
    排胶温度 = models.IntegerField(blank=True, null=True)
    排胶功率 = models.IntegerField(blank=True, null=True)
    排胶能量 = models.IntegerField(blank=True, null=True)
    作业方式 = models.CharField(max_length=8, blank=True, null=True)
    控制方式 = models.CharField(max_length=8, blank=True, null=True)
    员工代号 = models.CharField(max_length=18, blank=True, null=True)
    总重量 = models.IntegerField(blank=True, null=True)
    胶料重量 = models.IntegerField(blank=True, null=True)
    炭黑重量 = models.IntegerField(blank=True, null=True)
    油1重量 = models.IntegerField(blank=True, null=True)
    油2重量 = models.IntegerField(blank=True, null=True)
    计划号 = models.CharField(max_length=50, blank=True, null=True)
    配方号 = models.CharField(max_length=50, blank=True, null=True)
    加胶时间 = models.IntegerField(blank=True, null=True)
    加炭黑时间 = models.IntegerField(blank=True, null=True)
    加油1时间 = models.IntegerField(blank=True, null=True)
    加油2时间 = models.IntegerField(blank=True, null=True)
    存盘时间 = models.CharField(max_length=20, blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.CharField(db_column='RecStatus', max_length=20)

    class Meta:
        # managed = False
        db_table = 'ifup_report_basis_backups'


class IfupReportMixBackups(models.Model):
    """车次报表步序表"""
    序号 = models.BigAutoField(primary_key=True)
    步骤号 = models.IntegerField(blank=True, null=True)
    条件 = models.CharField(max_length=20, blank=True, null=True)
    时间 = models.IntegerField(blank=True, null=True)
    温度 = models.IntegerField(blank=True, null=True)
    功率 = models.IntegerField(blank=True, null=True)
    能量 = models.IntegerField(blank=True, null=True)
    动作 = models.CharField(max_length=20, blank=True, null=True)
    转速 = models.IntegerField(blank=True, null=True)
    压力 = models.IntegerField(blank=True, null=True)
    计划号 = models.CharField(max_length=50, blank=True, null=True)
    配方号 = models.CharField(max_length=50, blank=True, null=True)
    存盘时间 = models.CharField(max_length=20, blank=True, null=True)
    密炼车次 = models.IntegerField(blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.CharField(db_column='RecStatus', max_length=20)

    class Meta:
        # managed = False
        db_table = 'ifup_report_mix_backups'


class IfupReportCurveBackups(models.Model):
    """车次报表工艺曲线数据表"""
    序号 = models.BigAutoField(primary_key=True)
    计划号 = models.CharField(max_length=20, blank=True, null=True)
    配方号 = models.CharField(max_length=20, blank=True, null=True)
    温度 = models.IntegerField(blank=True, null=True)
    能量 = models.IntegerField(blank=True, null=True)
    功率 = models.IntegerField(blank=True, null=True)
    压力 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    转速 = models.IntegerField(blank=True, null=True)
    存盘时间 = models.CharField(max_length=20, blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.CharField(db_column='RecStatus', max_length=20)

    class Meta:
        # managed = False
        db_table = 'ifup_report_curve_backups'


class v_ASRS_STORE_MESVIEW(models.Model):
    """"""
    库房编号 = models.CharField(max_length=20, blank=True, null=True)
    库房名称 = models.CharField(max_length=20, blank=True, null=True)
    订单号 = models.CharField(max_length=50, blank=True, null=True)
    托盘号 = models.CharField(max_length=50, blank=True, null=True)
    货位地址 = models.CharField(max_length=20, blank=True, null=True)
    数量 = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    重量 = models.DecimalField(max_digits=15, decimal_places=3, blank=True, null=True)
    品质状态 = models.CharField(max_length=20, blank=True, null=True)
    车号 = models.CharField(max_length=250, blank=True, null=True)
    库存索引 = models.BigIntegerField()
    物料编码 = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "v_ASRS_STORE_MESVIEW"


class AlarmLog(AbstractEntity):
    """报警日志"""
    equip_no = models.CharField(max_length=64, help_text="机台号", verbose_name='机台号')
    content = models.TextField(max_length=1024, help_text="内容", verbose_name='内容')
    product_time = models.DateTimeField(help_text="报警时间", verbose_name='报警时间')

    class Meta:
        db_table = 'alarm_log'
        verbose_name_plural = verbose_name = '报警日志'
        indexes = [models.Index(fields=['equip_no']), models.Index(fields=['product_time'])]


class FeedingMaterialLog(models.Model):
    STATUS_CHOICE = (
        (1, '正常'),
        (2, '异常')
    )
    feed_uid = models.CharField(max_length=64, help_text='进料uid')
    equip_no = models.CharField(max_length=64, help_text='设备编号')
    plan_classes_uid = models.CharField(verbose_name='班次计划唯一码', help_text='班次计划唯一码', max_length=64)
    trains = models.IntegerField(help_text='车次')
    product_no = models.CharField(max_length=64, help_text='胶料名称')
    production_factory_date = models.DateField(max_length=64, help_text='工厂时间')
    production_classes = models.CharField(max_length=64, help_text='生产班次')
    production_group = models.CharField(max_length=64, help_text='生产班组')
    batch_time = models.DateTimeField(help_text='投入时间', null=True)
    batch_classes = models.CharField(max_length=64, help_text='投入班次', null=True)
    batch_group = models.CharField(max_length=64, help_text='投入班组', null=True)
    feedback_time = models.DateTimeField(help_text='重量反馈时间', null=True)
    feed_begin_time = models.DateTimeField(help_text='进料开始时间', null=True) #q
    feed_end_time = models.DateTimeField(help_text='进料结束时间', null=True)
    failed_flag = models.PositiveIntegerField(help_text='状态', choices=STATUS_CHOICE, default=1)
    judge_reason = models.CharField(max_length=255, help_text='防错结果', blank=True, null=True)
    feed_status = models.CharField(max_length=16, help_text='进料类型: 正常;处理;强制;', blank=True, null=True)
    add_feed_result = models.IntegerField(help_text='扫码补充物料后是否能进上辅机: 0 可进; 1 不可进;', blank=True, null=True)

    class Meta:
        db_table = 'feed_material_log'
        verbose_name_plural = verbose_name = '进料履历'


class LoadMaterialLog(models.Model):
    STATUS_CHOICE = (
        (1, '正常'),
        (2, '异常')
    )
    feed_log = models.ForeignKey(FeedingMaterialLog, on_delete=models.CASCADE)
    material_no = models.CharField(max_length=64, help_text='物料编码')
    material_name = models.CharField(max_length=64, help_text='物料名称')
    plan_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='计划重量', default=0)
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='实际重量', default=0)
    bra_code = models.CharField(max_length=64, help_text='条形码', blank=True, null=True)
    weight_time = models.DateTimeField(help_text='上料时间', null=True)
    status = models.PositiveIntegerField(help_text='状态', choices=STATUS_CHOICE, null=True)

    class Meta:
        db_table = 'load_material_log'
        verbose_name_plural = verbose_name = '上料履历'


class LoadTankMaterialLog(AbstractEntity):
    plan_classes_uid = models.CharField(max_length=64, help_text='小料称量计划号')
    scan_material = models.CharField(max_length=64, help_text='扫码物料名', default='')
    material_no = models.CharField(max_length=64, help_text='原材料编码')
    material_name = models.CharField(max_length=64, help_text='原材料名称')
    bra_code = models.CharField(max_length=64, help_text='条形码')
    unit = models.CharField(db_column='WeightUnit', max_length=64)
    scan_time = models.DateTimeField(max_length=64, help_text='扫码时间')
    useup_time = models.DateTimeField(max_length=64, help_text='用完时间')
    init_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='初始重量', default=0)
    # real_weight  修正剩余量后计算使用
    real_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='真实计算重量', default=0)
    actual_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='当前消耗重量', default=0)
    adjust_left_weight = models.DecimalField(decimal_places=2, max_digits=8, help_text='调整剩余重量', default=0)
    single_need = models.DecimalField(decimal_places=2, max_digits=8, help_text='单车需要物料数量', null=True, blank=True)
    variety = models.DecimalField(decimal_places=2, max_digits=8, help_text='物料修改变化量', null=True, blank=True, default=0)

    class Meta:
        db_table = 'load_tank_material_log'
        verbose_name_plural = verbose_name = '料框物料信息'
        managed = False
