from django.db import models

# Create your models here.
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models




class IfdownPmtRecipe1(models.Model):
    """1号机台配方主表"""
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    lasttime = models.CharField(max_length=19, blank=True, null=True) # 班日期
    oper = models.CharField(max_length=18, blank=True, null=True)  # 操作人角色
    recipe_code = models.CharField(max_length=14, blank=True, null=True)  # 配方编号
    recipe_name = models.CharField(max_length=20)  # 配方名称
    equip_code = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)  # 锁定/解锁
    reuse_time = models.IntegerField(blank=True, null=True)  # 回收时间
    mini_time = models.IntegerField(blank=True, null=True)   # 超温最短时间
    max_time = models.IntegerField(db_column='Max_time', blank=True, null=True)  # 超温最长时间
    mini_temp = models.IntegerField(blank=True, null=True)   # 进胶最低温度
    max_temp = models.IntegerField(blank=True, null=True)    # 进胶最高温度
    over_temp = models.IntegerField(blank=True, null=True)   # 超温温度
    if_not = models.IntegerField(blank=True, null=True)      # 是否回收
    temp_zz = models.IntegerField(blank=True, null=True)     # 转子水温
    temp_xlm = models.IntegerField(blank=True, null=True)    # 卸料门水温
    temp_cb = models.IntegerField(blank=True, null=True)     # 侧壁水温
    tempuse = models.IntegerField(blank=True, null=True)     # 三区水温启用/停用
    usenot = models.IntegerField(blank=True, null=True)      # 配方停用
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # 同步状态

    class Meta:
        managed = False
        db_table = 'ifdown_pmt_recipe_1'


class IfdownPmtRecipe2(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    lasttime = models.CharField(max_length=19, blank=True, null=True)
    oper = models.CharField(max_length=18, blank=True, null=True)
    recipe_code = models.CharField(max_length=14, blank=True, null=True)
    recipe_name = models.CharField(max_length=20)
    equip_code = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    reuse_time = models.IntegerField(blank=True, null=True)
    mini_time = models.IntegerField(blank=True, null=True)
    max_time = models.IntegerField(db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
    mini_temp = models.IntegerField(blank=True, null=True)
    max_temp = models.IntegerField(blank=True, null=True)
    over_temp = models.IntegerField(blank=True, null=True)
    if_not = models.IntegerField(blank=True, null=True)
    temp_zz = models.IntegerField(blank=True, null=True)
    temp_xlm = models.IntegerField(blank=True, null=True)
    temp_cb = models.IntegerField(blank=True, null=True)
    tempuse = models.IntegerField(blank=True, null=True)
    usenot = models.IntegerField(blank=True, null=True)
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_pmt_recipe_2'


class IfdownRecipeCb1(models.Model):
    """1号机台配方炭黑表"""
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)  # 炭黑名
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  #
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    recipe_name = models.CharField(max_length=20)   # 防错
    act_code = models.IntegerField(blank=True, null=True) # 动作编码
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_cb_1'


class IfdownRecipeCb2(models.Model):
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField(blank=True, null=True)
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_cb_2'


class IfdownRecipeMix1(models.Model):
    """1号机台配方步序表"""
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    set_condition = models.CharField(max_length=22, blank=True, null=True)  # 条件
    set_time = models.IntegerField(blank=True, null=True)    # 时间
    set_temp = models.IntegerField(blank=True, null=True)    # 温度
    set_ener = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)  # 能量
    set_power = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True) # 功率
    act_code = models.CharField(max_length=20)  # 动作
    set_pres = models.IntegerField(blank=True, null=True) # 压力
    set_rota = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True) # 转速
    recipe_name = models.CharField(max_length=20, blank=True, null=True)  # 配方名
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # 同步状态

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_mix_1'


class IfdownRecipeMix2(models.Model):
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    set_condition = models.CharField(max_length=22, blank=True, null=True)
    set_time = models.IntegerField(blank=True, null=True)
    set_temp = models.IntegerField(blank=True, null=True)
    set_ener = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    set_power = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    act_code = models.CharField(max_length=20)
    set_pres = models.IntegerField(blank=True, null=True)
    set_rota = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    recipe_name = models.CharField(max_length=20, blank=True, null=True)
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_mix_2'


class IfdownRecipeOil11(models.Model):
    """1号机台配方油料表"""
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)  # 油料名称
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # 设定重量
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # 防错
    recipe_name = models.CharField(max_length=20) # 配方名称
    act_code = models.IntegerField(blank=True, null=True) # 动作代码
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_oil1_1'


class IfdownRecipeOil12(models.Model):
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField(blank=True, null=True)
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_oil1_2'


class IfdownRecipePloy1(models.Model):
    """1号机台配方胶料表"""
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)  # 胶料名称
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True) # 防错？
    recipe_name = models.CharField(max_length=20)  # 配方名称
    act_code = models.IntegerField(blank=True, null=True) # 动作代码
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # 同步状态

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_ploy_1'


class IfdownRecipePloy2(models.Model):
    id = models.BigIntegerField(db_column='ID')  # Field name made lowercase.
    mname = models.CharField(max_length=19, blank=True, null=True)
    set_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    error_allow = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    recipe_name = models.CharField(max_length=20)
    act_code = models.IntegerField(blank=True, null=True)
    type = models.CharField(db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_recipe_ploy_2'


class IfdownShengchanjihua1(models.Model):
    """1号机台计划表"""
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    recipe = models.CharField(max_length=19)  # 配方名
    recipeid = models.CharField(max_length=19, blank=True, null=True)  # 配方编号
    lasttime = models.CharField(max_length=19, blank=True, null=True) # 班日期
    planid = models.CharField(max_length=19) # 计划编号  plan_no
    startime = models.CharField(max_length=19, blank=True, null=True)  # 开始时间
    stoptime = models.CharField(max_length=19, blank=True, null=True)  # 结束时间
    grouptime = models.CharField(max_length=10, blank=True, null=True)  # 班次
    groupoper = models.CharField(max_length=10, blank=True, null=True)  # 班组
    setno = models.IntegerField()  # 设定车次
    actno = models.IntegerField(blank=True, null=True)  # 当前车次
    oper = models.CharField(max_length=18, blank=True, null=True) # 操作员角色
    state = models.CharField(max_length=8, blank=True, null=True) # 计划状态：等待，运行中，完成
    remark = models.CharField(max_length=4)
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # 同步状态字段

    class Meta:
        managed = False
        db_table = 'ifdown_shengchanjihua_1'


class IfdownShengchanjihua2(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    recipe = models.CharField(max_length=19)
    recipeid = models.CharField(max_length=19, blank=True, null=True)
    lasttime = models.CharField(max_length=19, blank=True, null=True)
    planid = models.CharField(max_length=19)
    startime = models.CharField(max_length=19, blank=True, null=True)
    stoptime = models.CharField(max_length=19, blank=True, null=True)
    grouptime = models.CharField(max_length=10, blank=True, null=True)
    groupoper = models.CharField(max_length=10, blank=True, null=True)
    setno = models.IntegerField()
    actno = models.IntegerField(blank=True, null=True)
    oper = models.CharField(max_length=18, blank=True, null=True)
    state = models.CharField(max_length=8, blank=True, null=True)
    remark = models.CharField(max_length=4)
    recstatus = models.IntegerField(db_column='RecStatus', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifdown_shengchanjihua_2'


class IfupMachineStatus(models.Model):
    序号 = models.AutoField(primary_key=True)
    存盘时间 = models.CharField(max_length=20)
    计划号 = models.CharField(max_length=20, blank=True, null=True)
    配方号 = models.CharField(max_length=20, blank=True, null=True)
    运行状态 = models.IntegerField()
    机台号 = models.IntegerField()
    recstatus = models.IntegerField(db_column='RecStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifup_machine_status'


class IfupReportBasis(models.Model):
    序号 = models.AutoField(primary_key=True)
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
    油1重量= models.IntegerField(blank=True, null=True)
    油2重量 = models.IntegerField(blank=True, null=True)
    计划号 = models.CharField(max_length=50, blank=True, null=True)
    配方号 = models.CharField(max_length=50, blank=True, null=True)
    加胶时间 = models.IntegerField(blank=True, null=True)
    加炭黑时间 = models.IntegerField(blank=True, null=True)
    加油1时间 = models.IntegerField(blank=True, null=True)
    加油2时间 = models.IntegerField(blank=True, null=True)
    存盘时间 = models.CharField(max_length=20, blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.IntegerField(db_column='RecStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifup_report_basis'


class IfupReportCurve(models.Model):
    序号 = models.AutoField(primary_key=True)
    计划号 = models.CharField(max_length=20, blank=True, null=True)
    配方号 = models.CharField(max_length=20, blank=True, null=True)
    温度 = models.IntegerField(blank=True, null=True)
    能量 = models.IntegerField(blank=True, null=True)
    功率 = models.IntegerField(blank=True, null=True)
    压力 = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
    转速 = models.IntegerField(blank=True, null=True)
    存盘时间 = models.CharField(max_length=20, blank=True, null=True)
    机台号 = models.IntegerField()
    recstatus = models.IntegerField(db_column='RecStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifup_report_curve'


class IfupReportMix(models.Model):
    序号 = models.AutoField(primary_key=True)
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
    recstatus = models.IntegerField(db_column='RecStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifup_report_mix'


class IfupReportWeight(models.Model):
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
    recstatus = models.IntegerField(db_column='RecStatus')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ifup_report_weight'