# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/9/2
name: 
"""
import datetime
import os
import time

import django
import logging

from django.db.transaction import atomic



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from work_station.models import IfupReportCurve, IfupReportBasis, IfupReportMix, IfupReportWeight, IfupMachineStatus

def main():
    n = 1
    temp_list = [IfupReportCurve, IfupReportBasis, IfupReportMix, IfupReportWeight, IfupMachineStatus]
    product_time = datetime.datetime.now()
    recstatus = "待更新"
    plan_no = "2020090210271501Z05"
    recipe_no = "K-2MB-C150-01"
    equip_no = 5
    status = 1
    for m in temp_list:
        if m.__name__ == "IfupMachineStatus":
            """设备状态表"""
            data = {
                "存盘时间": product_time.strftime("%Y-%m-%d %H:%M:%S"),
                "计划号": plan_no,
                "配方号": recipe_no,
                "运行状态": status,
                "机台号": equip_no,
                "recstatus": recstatus
            }
        elif m.__name__ == "IfupReportBasis":
            """车次报表主信息"""
            data = {
                "车次号": n,
                "开始时间": (product_time - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "消耗时间": 5*60,
                "排胶时间": 10,
                "间隔时间": 5,
                "排胶温度": 100,
                "排胶功率": 100,
                "排胶能量": 100,
                "作业方式": "远程",
                "控制方式": "自动",
                "员工代号": "胡总",
                "总重量": 500,
                "胶料重量": 400,
                "炭黑重量": 40,
                "油1重量": 30,
                "油2重量": 30,
                "计划号": plan_no,
                "配方号": recipe_no,
                "加胶时间": 20,
                "加炭黑时间": 20,
                "加油1时间": 30,
                "加油2时间": 30,
                "存盘时间": product_time.strftime("%Y-%m-%d %H:%M:%S"),
                "机台号": equip_no,
                "recstatus": recstatus
            }
        elif m.__name__ == "IfupReportCurve":
            """车次报表工艺曲线数据表"""
            data = {
                "计划号": plan_no,
                "配方号": recipe_no,
                "温度": 200+n,
                "能量": 200+2*n,
                "功率": 200+n,
                "压力": 200+n*3,
                "转速": 500+n*3,
                "存盘时间": product_time.strftime("%Y-%m-%d %H:%M:%S"),
                "机台号": equip_no,
                "recstatus": recstatus,
            }
        elif m.__name__ == "IfupReportMix":
            """车次报表步序表"""
            data = {
                "步骤号": n,
                "条件": "demo",
                "时间": 300,
                "温度": 200+n,
                "功率": 200+n,
                "能量": 200+2*n,
                "动作": "上膛",
                "转速": 500+n*3,
                "压力": 200+n*3,
                "计划号": plan_no,
                "配方号": recipe_no,
                "存盘时间": product_time.strftime("%Y-%m-%d %H:%M:%S"),
                "密炼车次": n,
                "机台号": equip_no,
                "recstatus": recstatus,
            }
        elif m.__name__ == "IfupReportWeight":
            """车次报表材料重量表"""
            data = {
                "车次号": n,
                "物料名称": "wuliao1",
                "设定重量": 500,
                "实际重量": 500-n*10,
                "秤状态": "ok",
                "计划号": plan_no,
                "配方号": recipe_no,
                "物料编码": "SFS-10",
                "物料类型": "1",
                "存盘时间": product_time.strftime("%Y-%m-%d %H:%M:%S"),
                "机台号": equip_no,
                "recstatus": recstatus
            }
        else:
            data = {}
        m.objects.create(**data)

def run():
    while True:
        main()
        time.sleep(5)

if __name__ == '__main__':
    run()