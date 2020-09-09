# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/3
name: 
"""
import json

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


