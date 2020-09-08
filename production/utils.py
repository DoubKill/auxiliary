# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/3
name: 
"""

from io import BytesIO
import json
from datetime import datetime

import xlwt
from django.http import HttpResponse

from production.models import OperationLog
import re


class OpreationLogRecorder(object):

    def __init__(self, *args, **kwargs):
        self.equip_no = kwargs.get("equip_no", "")
        self.content = kwargs.get("content", {})
        temp_content = '{"message": "record log failed"}'
        if isinstance(self.content, dict):
            temp_content = json.dumps(self.content)
        self.data = dict(equip_no=self.equip_no, content=temp_content)

    def log_recoder(self):
        OperationLog.objects.create(**self.data)


def strtoint(equip_no):
    equip_list = re.findall(r'\d+', equip_no)
    equip_int = ''
    for i in equip_list:
        equip_int += i
    return int(equip_int)

def gen_material_export_file_response(filename: str, queryset):

    response = HttpResponse(content_type='application/vnd.ms-excel')
    # response['Content-Disposition'] = 'attachment;filename= ' + filename.encode('gbk').decode('ISO-8859-1') + '.xlsx'
    if queryset:
        # 创建工作簿
        ws = xlwt.Workbook(encoding='utf-8')
        # 添加第一页数据表
        w = ws.add_sheet('sheet1')  # 新建sheet（sheet的名称为"sheet1"）
        # 写入表头
        w.write(0, 0, u'id')
        w.write(0, 1, u'机台')
        w.write(0, 2, u'配方')
        w.write(0, 3, u'物料类别')
        w.write(0, 4, u'物料名称')
        w.write(0, 5, u'实际重量')
        # 写入数据
        excel_row = 1
        for obj in queryset:
            obj_id = obj['id']
            equip_no = obj['equip_no']
            product_no = obj['product_no']
            material_type = obj['material_type'] if obj['material_type'] else ''
            material_name = obj['material_name'] if obj['material_name'] else ''
            actual_weight = obj['actual_weight'] if obj['actual_weight'] else ''
            # 写入每一行对应的数据
            w.write(excel_row, 0, obj_id)
            w.write(excel_row, 1, equip_no)
            w.write(excel_row, 2, product_no)
            w.write(excel_row, 3, material_type)
            w.write(excel_row, 4, material_name)
            w.write(excel_row, 5, actual_weight)
            excel_row += 1
        # 写出到IO
        output = BytesIO()
        ws.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
    return response

