# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
from rest_framework import serializers

from mes.conf import COMMON_READ_ONLY_FIELDS
from work_station.models import IfdownPmtRecipe1


class IfdownPmtRecipe1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS
