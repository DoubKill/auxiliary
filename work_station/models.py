from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `# managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

# recstatus 字段主要为等待，运行中，完成
# 计划下达的过程中会有 配方需重传，车次需更新，配方车次需更新
from system.models import AbstractEntity


class SfjProducePlan(models.Model):
    """上辅机计划主表"""
    recipe_name = models.CharField(max_length=20)
    recipe_code = models.CharField(max_length=20)
    latesttime = models.DateTimeField()
    planid = models.CharField(max_length=20)
    starttime = models.DateTimeField()
    stoptime = models.DateTimeField()
    grouptime = models.CharField(max_length=10)
    groupoper = models.CharField(max_length=10)
    setno = models.IntegerField()
    finishno = models.IntegerField()
    oper = models.CharField(max_length=20)
    runstate = models.CharField(max_length=10)
    runmark = models.IntegerField()
    machineno = models.IntegerField()
    flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'produce_plan'



class SfjRecipeCon(models.Model):
    """上辅机配方主表"""
    latesttime = models.DateTimeField()
    oper = models.CharField(max_length=20)
    recipe_name = models.CharField(max_length=20)
    recipe_code = models.CharField(max_length=20)
    equip_code = models.DecimalField(max_digits=5, decimal_places=3)
    mini_time = models.IntegerField()
    max_time = models.IntegerField()
    mini_temp = models.IntegerField()
    max_temp = models.IntegerField()
    over_temp = models.IntegerField()
    reuse_time = models.IntegerField()
    if_not = models.IntegerField()
    rot_temp = models.IntegerField()
    shut_temp = models.IntegerField()
    side_temp = models.IntegerField()
    temp_on_off = models.IntegerField()
    sp_num = models.IntegerField()
    recipe_off = models.IntegerField()
    machineno = models.IntegerField()
    flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipe_con'


class SfjRecipeCb(models.Model):
    """上辅机炭黑配料表"""
    matname = models.CharField(max_length=32)
    matcode = models.CharField(max_length=32)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField()
    mattype = models.CharField(max_length=10)
    machineno = models.IntegerField()
    flag = models.IntegerField()


    class Meta:
        managed = False
        db_table = 'recipe_cb'


class SfjRecipeOil1(models.Model):
    """上辅机油配料表"""
    matname = models.CharField(max_length=32)
    matcode = models.CharField(max_length=32)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField()
    mattype = models.CharField(max_length=10)
    machineno = models.IntegerField()
    flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipe_oil1'


class SfjRecipeGum(models.Model):
    """上辅机炭胶料料表"""
    matname = models.CharField(max_length=32)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField()
    mattype = models.CharField(max_length=10)
    machineno = models.IntegerField()
    flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipe_gum'


class SfjRecipeMix(models.Model):
    """上辅机炭黑配料表"""
    recipe_name = models.CharField(max_length=20)
    set_condition = models.CharField(max_length=20)
    set_time = models.IntegerField()
    set_temp = models.IntegerField()
    set_ener = models.DecimalField(max_digits=5, decimal_places=1)
    set_power = models.DecimalField(max_digits=5, decimal_places=1)
    act_code = models.CharField(max_length=20)
    set_pres = models.IntegerField()
    set_rota = models.IntegerField()
    ID_step = models.IntegerField()
    machineno = models.IntegerField()
    flag = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'recipe_mix'


class SfjAlarmLog(models.Model):

    machineno = models.IntegerField(help_text="机台号", verbose_name='机台号')
    content = models.CharField(max_length=50, help_text="内容", verbose_name='内容')
    latesttime = models.DateTimeField(help_text="报警时间", verbose_name='报警时间')

    class Meta:
        managed = False
        db_table = 'report_alarm'


class SfjEquipStatus(models.Model):
    """机台状况反馈"""
    plan_classes_uid = models.CharField(help_text='班次计划唯一码', verbose_name='班次计划唯一码', max_length=25, null=True)
    equip_no = models.CharField(max_length=5, help_text="机台号", verbose_name='机台号', null=True)
    temperature = models.IntegerField(help_text='温度', verbose_name='温度', null=True)
    rpm = models.IntegerField(help_text='转速', verbose_name='转速', null=True)
    energy = models.IntegerField(help_text='能量', verbose_name='能量', null=True)
    power = models.IntegerField(help_text='功率', verbose_name='功率', null=True)
    pressure = models.IntegerField(help_text='压力', verbose_name='压力', null=True)
    status = models.CharField(max_length=10, help_text='状态：运行中、等待、故障', verbose_name='状态', default="运行中", null=True)
    current_trains = models.IntegerField(help_text='当前车次', verbose_name='当前车次', null=True)
    product_time = models.DateTimeField(help_text='工作站生产报表时间/存盘时间', verbose_name='工作站生产报表时间/存盘时间', null=True)
    flag = models.IntegerField()
    created_date = models.DateTimeField(verbose_name='创建时间', blank=True, null=True)
    last_updated_date = models.DateTimeField(verbose_name='修改时间', blank=True, null=True)
    delete_date = models.DateTimeField(blank=True, null=True, help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)


    class Meta:
        managed = False
        db_table = 'equip_status'


class I_RECIPES_V(models.Model):
    """Z04配方视图"""
    recipe_id = models.AutoField(primary_key=True)
    line_name = models.CharField(null=True, blank=True,max_length=20)
    recipe_number = models.CharField(null=True, blank=True,max_length=240)
    recipe_code = models.CharField(null=True, blank=True,max_length=30)
    recipe_version = models.IntegerField(null=True, blank=True,)
    recipe_description = models.CharField(null=True, blank=True,max_length=240)
    recipe_blocked = models.CharField(null=True, blank=True,max_length=20)
    last_changed_date = models.DateTimeField(null=True, blank=True,)
    recipe_type = models.CharField(null=True, blank=True,max_length=240)

    class Meta:
        managed = False
        db_table = 'i_recipes_v'


class ProdOrdersImp(models.Model):
    """Z04计划交互"""
    pori_id = models.AutoField(primary_key=True)
    pori_pror_id = models.IntegerField(null=True, blank=True,)
    pori_host_id = models.IntegerField(null=True, blank=True,)
    pori_line_name = models.CharField(null=True, blank=True,max_length=30)
    pori_order_number = models.CharField(null=True, blank=True,max_length=30)
    pori_sequence_id = models.CharField(null=True, blank=True,max_length=30)
    pori_order_stage = models.IntegerField(null=True, blank=True,)
    pori_order_stage_id = models.CharField(null=True, blank=True,max_length=30)
    pori_auto_orderchange_flag = models.IntegerField(null=True, blank=True,)
    pori_recipe_code = models.CharField(null=True, blank=True,max_length=30)
    pori_recipe_version = models.IntegerField(null=True, blank=True,)
    pori_article_number = models.CharField(null=True, blank=True,max_length=30)
    pori_batch_quantity_set = models.IntegerField(null=True, blank=True,)
    pori_order_weight = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    pori_cust_batch_prefix = models.CharField(null=True, blank=True,max_length=30)
    pori_cust_batch_counter = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    pori_cust_batch_suffix = models.CharField(null=True, blank=True,max_length=30)
    pori_start_date = models.DateTimeField(null=True, blank=True,)
    pori_end_date = models.DateTimeField(null=True, blank=True,)
    pori_pror_blocked = models.IntegerField(null=True, blank=True,)
    pori_batch_quantity_act = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    pori_pror_status = models.IntegerField(default=0)
    pori_order_weight_act = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    pori_start_date_act = models.DateTimeField(null=True, blank=True,)
    pori_end_date_act = models.DateTimeField(null=True, blank=True,)
    pori_stock_number = models.CharField(null=True, blank=True,max_length=240)
    pori_function = models.IntegerField(null=True, blank=True,)
    pori_status = models.IntegerField(default=0)
    pori_freetext_1 = models.TextField(null=True, blank=True,max_length=1000)
    pori_freetext_2 = models.TextField(null=True, blank=True,max_length=1000)
    pori_goods_recipient = models.CharField(null=True, blank=True,max_length=240)
    pori_unloading_point = models.CharField(null=True, blank=True,max_length=240)
    pori_planning_blocked = models.IntegerField(null=True, blank=True,)
    insert_user = models.CharField(null=True, blank=True,max_length=30)
    insert_date = models.DateTimeField(null=True, blank=True,)
    update_user = models.CharField(null=True, blank=True,max_length=30)
    update_date = models.DateTimeField(null=True, blank=True,)

    class Meta:
        managed = False
        db_table = 'prod_orders_imp'


class LogTable(models.Model):
    """Z04错误日志"""
    lgtb_id = models.AutoField(primary_key=True)
    lgtb_username = models.CharField(null=True, blank=True,max_length=240)
    lgtb_date = models.DateTimeField(null=True, blank=True,)
    lgtb_action = models.TextField(null=True, blank=True,max_length=1000)
    lgtb_sql_errormessage = models.TextField(null=True, blank=True,max_length=1000)
    lgtb_pks_errormessage = models.TextField(null=True, blank=True,max_length=1000)
    lgtb_return_status = models.IntegerField(null=True, blank=True,)
    lgtb_host_id = models.IntegerField(null=True, blank=True,)
    lgtb_transfer_table_ident = models.CharField(null=True, blank=True,max_length=240)
    insert_user = models.CharField(null=True, blank=True,max_length=30)
    insert_date = models.DateTimeField(null=True, blank=True,)
    update_user = models.CharField(null=True, blank=True,max_length=30)
    update_date = models.DateTimeField(null=True, blank=True,)

    class Meta:
        managed = False
        db_table = "log_table"


class BatchReport(models.Model):
    """批次报表数据"""
    batr_id = models.AutoField(primary_key=True)
    batr_host_id = models.IntegerField(null=True, blank=True,)
    batr_line_name = models.CharField(null=True, blank=True,max_length=30)
    batr_camp_number = models.CharField(null=True, blank=True,max_length=30)
    batr_recipe_group = models.CharField(null=True, blank=True,max_length=30)
    batr_order_id = models.IntegerField(null=True, blank=True,)
    batr_order_number = models.CharField(null=True, blank=True,max_length=30)
    batr_order_stage = models.IntegerField(null=True, blank=True,)
    batr_batch_quantity_set = models.IntegerField(null=True, blank=True,)
    batr_batch_id = models.IntegerField(null=True, blank=True,)
    batr_batch_number = models.IntegerField(null=True, blank=True,)
    batr_batch_customer_name = models.CharField(null=True, blank=True,max_length=240)
    batr_batch_code = models.CharField(null=True, blank=True,max_length=30)
    batr_batch_code_packing_id = models.CharField(null=True, blank=True,max_length=30)
    batr_recipe_id = models.IntegerField(null=True, blank=True,)
    batr_recipe_code = models.CharField(null=True, blank=True,max_length=30)
    batr_recipe_version = models.IntegerField(null=True, blank=True,)
    batr_article_number = models.CharField(null=True, blank=True,max_length=30)
    batr_stock_number = models.CharField(null=True, blank=True,max_length=240)
    batr_batch_weight = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_batch_weight_act = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_start_date = models.DateTimeField(null=True, blank=True,)
    batr_end_date = models.DateTimeField(null=True, blank=True,)
    batr_station_ident = models.CharField(null=True, blank=True,max_length=240)
    batr_quality = models.IntegerField(null=True, blank=True,)
    batr_total_spec_energy = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_tot_integr_energy = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_total_revolutions = models.IntegerField(null=True, blank=True,)
    batr_ram_distance = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_cycle_time = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_drop_cycle_time = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_mixing_time = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_time_ram_pressing = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_time_ram_down = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_transition_temperature = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_tc1 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_tc2 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_tc3 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_chamber1 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_chamber2 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_water_tcu1 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_water_tcu2 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_water_tcu3 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_temp_water_tcu4 = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_drive_current = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_drive_power = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    batr_packing_date = models.DateTimeField(null=True, blank=True,)
    batr_expiration_date = models.DateTimeField(null=True, blank=True,)
    batr_user_id = models.IntegerField(null=True, blank=True,)
    batr_user_name = models.CharField(null=True, blank=True,max_length=30)
    batr_release_date = models.DateTimeField(null=True, blank=True,)
    batr_release_status = models.IntegerField(null=True, blank=True,)
    batr_batch_duration = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    insert_user = models.CharField(null=True, blank=True,max_length=30)
    insert_date = models.DateTimeField(null=True, blank=True,)
    update_user = models.CharField(null=True, blank=True,max_length=30)
    update_date = models.DateTimeField(null=True, blank=True,)
    batr_measured_data = models.TextField(null=True, blank=True, )


    class Meta:
        managed = False
        db_table = "batch_report"


class MaterialsConsumption(models.Model):
    """消耗报表"""
    maco_id = models.AutoField(primary_key=True)
    maco_date = models.DateTimeField(null=True, blank=True,)
    maco_line_name = models.CharField(null=True, blank=True,max_length=30)
    maco_camp_number = models.CharField(null=True, blank=True,max_length=30)
    maco_order_id = models.IntegerField(null=True, blank=True,)
    maco_order_number = models.CharField(null=True, blank=True,max_length=30)
    maco_order_stage = models.IntegerField(null=True, blank=True,)
    maco_batch_id = models.IntegerField(null=True, blank=True,)
    maco_batch_number = models.IntegerField(null=True, blank=True,)
    maco_batch_customer_name = models.CharField(null=True, blank=True,max_length=240)
    maco_mat_code = models.CharField(null=True, blank=True,max_length=240)
    maco_packing_id = models.CharField(null=True, blank=True,max_length=30)
    maco_raw_material_id = models.IntegerField(null=True, blank=True,)
    maco_lot_number = models.CharField(null=True, blank=True,max_length=240)
    maco_consumed_quantity = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    maco_start_date = models.DateTimeField(null=True, blank=True,)
    maco_end_date = models.DateTimeField(null=True, blank=True,)
    maco_station_ident = models.CharField(null=True, blank=True,max_length=30)
    maco_host = models.CharField(null=True, blank=True,max_length=30)
    maco_recipe_id = models.IntegerField(null=True, blank=True,)
    maco_recipe_code = models.CharField(null=True, blank=True,max_length=30)
    maco_recipe_version = models.IntegerField(null=True, blank=True,)
    maco_recipe_group = models.CharField(null=True, blank=True,max_length=30)
    maco_set_quantity = models.DecimalField(null=True, blank=True,max_digits=12, decimal_places=6)
    insert_user = models.CharField(null=True, blank=True,max_length=30)
    insert_date = models.DateTimeField(null=True, blank=True,)
    update_user = models.CharField(null=True, blank=True,max_length=30)
    update_date = models.DateTimeField(null=True, blank=True,)

    class Meta:
        managed = False
        db_table = "materials_consumption"


class I_ORDER_STATE_V(models.Model):
    """计划订单状态视图"""
    order_id = models.IntegerField(primary_key=True)
    order_name = models.CharField(max_length=240)
    recipe_id = models.IntegerField()
    recipe = models.CharField(max_length=30)
    recipe_code = models.CharField(max_length=30)
    recipe_name = models.CharField(max_length=240)
    recipe_version = models.IntegerField()
    recipe_weight = models.DecimalField(max_digits=12, decimal_places=3)
    order_sequence = models.IntegerField()
    order_freetext_1 = models.TextField(max_length=1000)
    order_freetext_2 = models.TextField(max_length=1000)
    batches_set = models.IntegerField()
    batches_act = models.IntegerField()
    order_auto_change = models.CharField(max_length=1)
    planned_start_date = models.DateTimeField()
    order_start_date = models.DateTimeField()
    order_end_date = models.DateTimeField()
    order_released = models.IntegerField()
    order_insert_date = models.DateTimeField()
    order_weight = models.DecimalField(max_digits=12, decimal_places=3)
    order_weight_act = models.DecimalField(max_digits=12, decimal_places=3)
    station_ident = models.CharField(max_length=100)
    station_name = models.CharField(max_length=30)
    line_name = models.CharField(max_length=240)
    order_status = models.CharField(max_length=240)

    class Meta:
        managed = False
        db_table = 'i_order_state_v'

class I_RECIPE_COMPONENTS_V(models.Model):
    """配方称量视图"""
    reco_id = models.IntegerField(primary_key=True)
    line_aggregate = models.CharField(max_length=64, help_text="串行密炼机类型")
    weight = models.DecimalField(max_digits=12, decimal_places=3, help_text="原材料重量")
    recipe_number = models.CharField(max_length=64, help_text="配方编号")
    recipe_version = models.IntegerField(help_text="配方版本")
    production_line_name = models.CharField(max_length=64, help_text="机台号")

    class Meta:
        managed = False
        db_table = 'i_recipe_components_v'