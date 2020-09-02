
# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
from rest_framework.exceptions import ValidationError

from work_station import serializers as sz
from work_station import models as md


class IssueWorkStation(object):

    def __init__(self, model_name, data):
        """
        传入对应的模型类与数据
        data 传入带id数据为修改中间表数据，
             不传入则为新增
        """
        self.model = getattr(md, model_name)
        self.model_name = model_name
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
        # TODO 判断recstatus进行分支处理
        serializer = self.model_serializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # self.model.objects.create(**self.data)

    def batch_to_db(self):
        """
        对接万隆中间表
        将数据批量存入到中间表
        """
        # model_data = [self.model(**_) for _ in self.data]
        # self.model.objects.bulk_create(model_data)
        serializer = self.model_serializer(data=self.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()


    def update_to_db(self):
        """
        对接中间表用于修改数据
        """
        id = self.data.get("id")
        instance = self.model.objects.filter(id=id).first()
        serializer = self.model_serializer(instance, data=self.data, partial="partial")
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def batch_update_to_db(self):
        """
        批量更新中间表数据
        """
        for _ in self.data:
            id = _.get("id")
            instance = self.model.objects.filter(id=id).first()
            if instance.recstatus == "车次需更新":
                _["recstatus"] = "配方车次需更新"
            elif instance.recstatus == "运行中":
                _["recstatus"] = "配方需重传"
            elif instance.recstatus == "配方车次需更新":
                pass
            else:
                raise ValidationError("异常接收状态,仅运行中状态允许重传")
            serializer = self.model_serializer(instance, data=self.data, partial="partial")
            serializer.is_valid(raise_exception=True)
            serializer.save()

    def issue_to_interface(self):
        """对接api"""
        pass