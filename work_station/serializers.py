# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
from rest_framework import serializers

from mes.conf import COMMON_READ_ONLY_FIELDS
from work_station.models import *


class IfdownPmtRecipe1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe2Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeCb1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb2Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeCb2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeMix1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix2Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeMix2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil11Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeOil11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil12Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeOil12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipePloy1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy2Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipePloy2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua1Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownShengchanjihua1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua2Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownShengchanjihua2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfupMachineStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = IfupMachineStatus
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfupReportBasisSerializer(serializers.ModelSerializer):

    class Meta:
        model = IfupReportBasis
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfupReportCurveSerializer(serializers.ModelSerializer):

    class Meta:
        model = IfupReportCurve
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfupReportMixSerializer(serializers.ModelSerializer):

    class Meta:
        model = IfupReportMix
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfupReportWeightSerializer(serializers.ModelSerializer):

    class Meta:
        model = IfupReportWeight
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS