# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import requests
from rest_framework.exceptions import ValidationError

from work_station import serializers as sz
from work_station import models as md


class IssueWorkStation(object):

    def __init__(self, model_name, data, ext_str=None):
        """
        传入对应的模型类与数据
        data 传入带id数据为修改中间表数据，
             不传入则为新增
        """
        self.model = getattr(md, model_name)
        self.model_name = model_name
        self.data = data
        self.ext_str = ext_str
        self.plan_model = getattr(md, "IfdownShengchanjihua" + self.ext_str)

    @property
    def model_serializer(self):
        """自动匹配序列化器"""
        return getattr(sz, f"{self.model_name}Serializer")

    def issue_to_db(self):
        """
        对接万隆中间表
        将数据存入到中间表
        """
        if self.plan_model.objects.filter(recstatus__in=["等待", "运行中", "车次需更新", "配方车次需更新", "配方需重传", "待停止"]).exists():
            raise ValidationError("该机台中存在已下达/运行中/待停止的计划，请停止计划或等待计划完成后再下达")
        if self.plan_model.objects.filter(recstatus__in=["完成", "停止"]).exists():
            self.model.objects.filter().delete()
        serializer = self.model_serializer(data=self.data)
        serializer.is_valid()
        try:
            serializer.save()
        except:
            raise ValidationError("该机台中存在已下达/运行中的计划，请停止计划或等待计划完成后再下达")

    def batch_to_db(self):
        """
        对接万隆中间表
        将数据批量存入到中间表
        """
        # model_data = [self.model(**_) for _ in self.data]
        # self.model.objects.bulk_create(model_data)
        if self.plan_model.objects.filter(recstatus__in=["等待", "运行中", "车次需更新", "配方车次需更新", "配方需重传", "待停止"]).exists():
            raise ValidationError("该机台中存在已下达/运行中的计划，请停止计划或等待计划完成后再下达")
        if self.plan_model.objects.filter(recstatus__in=["完成", "停止"]).exists():
            self.model.objects.filter().delete()
        serializer = self.model_serializer(data=self.data, many=True)
        serializer.is_valid()
        try:
            serializer.save()
        except:
            raise ValidationError("该机台中存在已下达/运行中的计划，请停止计划或等待计划完成后再下达")

    def update_to_db(self, flag=False):
        """
        对接中间表用于修改数据
        """
        if self.plan_model.objects.filter(recstatus__in=["等待"]).exists():
            raise ValidationError("等待状态中的计划，无法修改工作站车次")
        id = self.data.get("id")
        instance = self.model.objects.filter(id=id).first()
        if not instance:
            raise ValidationError(f"未检测到该计划/配方|{self.model_name}|下达")
        if flag:
            if instance.recstatus == "车次需更新":
                self.data["recstatus"] = "车次需更新"
            elif instance.recstatus == "运行中":
                self.data["recstatus"] = "车次需更新"
            elif instance.recstatus == "配方车次需更新":
                self.data["recstatus"] = "配方车次需更新"
            elif instance.recstatus == '配方需重传':
                self.data["recstatus"] = "配方车次需更新"
            else:
                self.data["recstatus"] = '配方需重传'
        else:
            if instance.recstatus == "车次需更新":
                self.data["recstatus"] = "配方车次需更新"
            elif instance.recstatus == "运行中":
                self.data["recstatus"] = '配方需重传'
            elif instance.recstatus == "配方车次需更新":
                self.data["recstatus"] = "配方车次需更新"
            elif instance.recstatus == '配方需重传':
                self.data["recstatus"] = '配方需重传'
            else:
                self.data["recstatus"] = '配方需重传'
        self.model.objects.filter().delete()
        serializer = self.model_serializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def batch_update_to_db(self):
        """
        批量更新中间表数据
        """
        if self.plan_model.objects.filter(recstatus__in=["等待"]).exists():
            raise ValidationError("等待状态中的计划，无法修改工作站车次")
        for _ in self.data:
            id = _.get("id")
            instance = self.model.objects.filter(id=id).first()
            if instance:
                if instance.recstatus == "车次需更新":
                    _["recstatus"] = "配方车次需更新"
                elif instance.recstatus == "运行中":
                    _["recstatus"] = "配方需重传"
                elif instance.recstatus == "配方需重传":
                    _["recstatus"] = "配方需重传"
                elif instance.recstatus == "配方车次需更新":
                    _["recstatus"] = "配方车次需更新"
                else:
                    _["recstatus"] = "配方需重传"
        self.model.objects.filter().delete()
        serializer = self.model_serializer(data=self.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
