
# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
import importlib

from work_station import models as md
from work_station import serializers as sz


def _model_serializer(model):
    return getattr(sz, f"{model.__name__}Serializer")


class IssueWorkStation(object):

    def __init__(self):
        pass

    def _model_name(self):
        pass

    def _model_serializer(self, model):
        return getattr(sz, f"{model.__name__}Serializer")

    def issue(self):
        """
        """
        # mid_recipe = getattr(md, f"IfdownPmtRecipe{equip_no}")
        # erializer = self._model_serializer()
        pass
        # if data.get("id"):

