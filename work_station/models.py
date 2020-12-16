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


# class IfdownPmtRecipe1(models.Model):
#     """1号机台配方主表"""
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True) # 班日期
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)  # 操作人角色
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)  # 配方编号
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)  # 锁定/解锁
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 回收时间
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)   # 超温最短时间
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # 炼胶超时时间
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)   # 进胶最低温度
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)    # 进胶最高温度
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)   # 超温温度
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)      # 是否回收
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)     # 转子水温
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)    # 卸料门水温
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)     # 侧壁水温
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)     # 三区水温启用/停用
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)      # 配方停用
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_1'


# class IfdownPmtRecipe2(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_2'


# class IfdownPmtRecipe3(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_3'


# class IfdownPmtRecipe4(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_4'


# class IfdownPmtRecipe5(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_5'


# class IfdownPmtRecipe6(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_6'


# class IfdownPmtRecipe7(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_7'


# class IfdownPmtRecipe8(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_8'


# class IfdownPmtRecipe9(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_9'


# class IfdownPmtRecipe10(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_10'


# class IfdownPmtRecipe11(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_11'


# class IfdownPmtRecipe12(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_12'


# class IfdownPmtRecipe13(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_13'


# class IfdownPmtRecipe14(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_14'


# class IfdownPmtRecipe15(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     recipe_code = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)
#     equip_code = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=3, blank=True, null=True)
#     reuse_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     mini_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_time = models.IntegerField(null=True, blank=True,db_column='Max_time', blank=True, null=True)  # Field name made lowercase.
#     mini_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     max_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     over_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     if_not = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_zz = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_xlm = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     temp_cb = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     tempuse = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     usenot = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_pmt_recipe_15'







# class IfdownRecipeMix1(models.Model):
#     """1号机台配方步序表"""
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)  # 条件
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)    # 时间
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)    # 温度
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)  # 能量
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True) # 功率
#     act_code = models.CharField(null=True, blank=True,max_length=20)  # 动作
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True) # 压力
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True) # 转速
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)  # 配方名
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_1'


# class IfdownRecipeMix2(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_2'


# class IfdownRecipeMix3(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_3'


# class IfdownRecipeMix4(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_4'


# class IfdownRecipeMix5(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_5'


# class IfdownRecipeMix6(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_6'


# class IfdownRecipeMix7(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_7'


# class IfdownRecipeMix8(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_8'


# class IfdownRecipeMix9(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_9'


# class IfdownRecipeMix10(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_10'



# class IfdownRecipeMix11(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_11'


# class IfdownRecipeMix12(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_12'


# class IfdownRecipeMix13(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_13'


# class IfdownRecipeMix14(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_14'


# class IfdownRecipeMix15(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     set_condition = models.CharField(null=True, blank=True,max_length=22, blank=True, null=True)
#     set_time = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_temp = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_ener = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     set_power = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     act_code = models.CharField(null=True, blank=True,max_length=20)
#     set_pres = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     set_rota = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     recipe_name = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_mix_15'


# class IfdownRecipeWeigh1(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_1'


# class IfdownRecipeWeigh2(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_2'


# class IfdownRecipeWeigh3(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_3'


# class IfdownRecipeWeigh4(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_4'


# class IfdownRecipeWeigh5(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_5'


# class IfdownRecipeWeigh6(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_6'


# class IfdownRecipeWeigh7(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_7'


# class IfdownRecipeWeigh8(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_8'


# class IfdownRecipeWeigh9(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_9'


# class IfdownRecipeWeigh10(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_10'


# class IfdownRecipeWeigh11(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_11'


# class IfdownRecipeWeigh12(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_12'


# class IfdownRecipeWeigh13(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_13'


# class IfdownRecipeWeigh14(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_14'


# class IfdownRecipeWeigh15(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     mname = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 油料名称
#     set_weight = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 设定重量
#     error_allow = models.DecimalField(null=True, blank=True,max_digits=10, decimal_places=2, blank=True, null=True)  # 防错
#     recipe_name = models.CharField(null=True, blank=True,max_length=20)  # 配方名称
#     act_code = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 动作代码
#     type = models.CharField(null=True, blank=True,db_column='TYPE', max_length=1, blank=True, null=True)  # Field name made lowercase.
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_recipe_weigh_15'


# class IfdownShengchanjihua1(models.Model):
#     """1号机台计划表"""
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)  # 配方名
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 配方编号
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True) # 班日期
#     planid = models.CharField(null=True, blank=True,max_length=36) # 计划编号  plan_no
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 开始时间
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)  # 结束时间
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)  # 班次
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)  # 班组
#     setno = models.IntegerField(null=True, blank=True,)  # 设定车次
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)  # 当前车次
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True) # 操作员角色
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True) # 计划状态：等待，运行中，完成
#     remark = models.CharField(null=True, blank=True,max_length=4) # c 新增  u 更新 d删除
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_1'


# class IfdownShengchanjihua2(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_2'


# class IfdownShengchanjihua3(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_3'


# class IfdownShengchanjihua4(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_4'


# class IfdownShengchanjihua5(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_5'


# class IfdownShengchanjihua6(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_6'


# class IfdownShengchanjihua7(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_7'


# class IfdownShengchanjihua8(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_8'


# class IfdownShengchanjihua9(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_9'


# class IfdownShengchanjihua10(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_10'


# class IfdownShengchanjihua11(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_11'


# class IfdownShengchanjihua12(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_12'


# class IfdownShengchanjihua13(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_13'


# class IfdownShengchanjihua14(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_14'


# class IfdownShengchanjihua15(models.Model):
#     id = models.BigIntegerField(null=True, blank=True,db_column='ID', primary_key=True)  # Field name made lowercase.
#     recipe = models.CharField(null=True, blank=True,max_length=19)
#     recipeid = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     lasttime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     planid = models.CharField(null=True, blank=True,max_length=19)
#     startime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     stoptime = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     grouptime = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     groupoper = models.CharField(null=True, blank=True,max_length=10, blank=True, null=True)
#     setno = models.IntegerField(null=True, blank=True,)
#     actno = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     oper = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     state = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     remark = models.CharField(null=True, blank=True,max_length=4)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifdown_shengchanjihua_15'


# class IfupMachineStatus(models.Model):
#     """设备状态表"""
#     序号 = models.BigAutoField(null=True, blank=True,primary_key=True)
#     存盘时间 = models.CharField(null=True, blank=True,max_length=20) # 上辅机或者mes是否需要
#     计划号 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)  # plan_no?
#     配方号 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)  # recipe no
#     运行状态 = models.IntegerField(null=True, blank=True,)
#     机台号 = models.IntegerField(null=True, blank=True,)  # equip_no
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifup_machine_status'


# class IfupReportBasis(models.Model):
#     """车次报表主信息"""
#     序号 = models.BigAutoField(null=True, blank=True,primary_key=True)
#     车次号 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     开始时间 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     消耗时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     排胶时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     间隔时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     排胶温度 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     排胶功率 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     排胶能量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     作业方式 = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     控制方式 = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     员工代号 = models.CharField(null=True, blank=True,max_length=18, blank=True, null=True)
#     总重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     胶料重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     炭黑重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     油1重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     油2重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     计划号 = models.CharField(null=True, blank=True,max_length=50, blank=True, null=True)
#     配方号 = models.CharField(null=True, blank=True,max_length=50, blank=True, null=True)
#     加胶时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     加炭黑时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     加油1时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     加油2时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     存盘时间 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     机台号 = models.IntegerField(null=True, blank=True,)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifup_report_basis'


# class IfupReportCurve(models.Model):
#     """车次报表工艺曲线数据表"""
#     序号 = models.BigAutoField(null=True, blank=True,primary_key=True)
#     计划号 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     配方号 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     温度 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     能量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     功率 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     压力 = models.DecimalField(null=True, blank=True,max_digits=5, decimal_places=1, blank=True, null=True)
#     转速 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     存盘时间 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     机台号 = models.IntegerField(null=True, blank=True,)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifup_report_curve'


# class IfupReportMix(models.Model):
#     """车次报表步序表"""
#     序号 = models.BigAutoField(null=True, blank=True,primary_key=True)
#     步骤号 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     条件 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     时间 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     温度 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     功率 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     能量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     动作 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     转速 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     压力 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     计划号 = models.CharField(null=True, blank=True,max_length=50, blank=True, null=True)
#     配方号 = models.CharField(null=True, blank=True,max_length=50, blank=True, null=True)
#     存盘时间 = models.CharField(null=True, blank=True,max_length=20, blank=True, null=True)
#     密炼车次 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     机台号 = models.IntegerField(null=True, blank=True,)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifup_report_mix'


# class IfupReportWeight(models.Model):
#     """车次报表材料重量表"""
#     序号 = models.BigAutoField(null=True, blank=True,primary_key=True)
#     车次号 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     物料名称 = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     设定重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     实际重量 = models.IntegerField(null=True, blank=True,blank=True, null=True)
#     秤状态 = models.CharField(null=True, blank=True,max_length=8, blank=True, null=True)
#     计划号 = models.CharField(null=True, blank=True,max_length=50)
#     配方号 = models.CharField(null=True, blank=True,max_length=50)
#     物料编码 = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     物料类型 = models.CharField(null=True, blank=True,max_length=1, blank=True, null=True)
#     存盘时间 = models.CharField(null=True, blank=True,max_length=19, blank=True, null=True)
#     机台号 = models.IntegerField(null=True, blank=True,)
#     recstatus = models.CharField(null=True, blank=True,db_column='RecStatus', max_length=30)
#
#     class Meta:
#         # managed = False
#         db_table = 'ifup_report_weight'


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
        # managed = False
        db_table = 'i_recipes_v'


class ProdOrdersImp(models.Model):

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
    pori_pror_status = models.IntegerField(null=True, blank=True,)
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
        # managed = False
        db_table = 'prod_orders_imp'


class LogTable(models.Model):

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
        # managed = False
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


    class Meta:
        # managed = False
        db_table = "batch_report"


class EquipRunData(models.Model):
    """用于单独从批次报表中获取曲线数据"""
    batr_id = models.AutoField(primary_key=True)
    batr_measured_data = models.TextField(null=True, blank=True,)

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
        # managed = False
        db_table = "materials_consumption"