
# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""

from work_station import serializers as sz


class IssueWorkStation(object):

    def __init__(self, model, data):
        """
        传入对应的模型类与数据
        data 传入带id数据为修改中间表数据，
             不传入则为新增
        """
        self.model = model
        self.model_name = model.__name__
        self.data = data

    @property
    def model_serializer(self):
        """自动匹配序列化器"""
        return getattr(sz, f"{self.model_name}Serializer")

    def issue_to_db(self):
        """
        对接万隆中间表
        将数据存入到中间表
        """
        id = self.data.get("id")
        if id:
            instance = self.model.objects.filter(id=id).first()
            serializer = self.model_serializer(instance, data=self.data, partial="partial")
        else:
            serializer = self.model_serializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def issue_to_interface(self):
        """对接国自组态"""
        pass


class UploadAuxiliary(object):

    def __init__(self):
        pass