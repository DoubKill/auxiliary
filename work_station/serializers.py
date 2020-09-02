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

class IfdownPmtRecipe3Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

class IfdownPmtRecipe4Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

class IfdownPmtRecipe5Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe5
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

class IfdownPmtRecipe6Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownPmtRecipe6
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


class IfdownRecipeCb3Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeCb3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb4Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeCb4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb5Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeCb5
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


class IfdownRecipeMix3Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeMix3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix4Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeMix4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix5Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeMix5
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


class IfdownRecipeOil13Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeOil13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

class IfdownRecipeOil14Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeOil14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil15Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipeOil15
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


class IfdownRecipePloy3Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipePloy3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy4Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipePloy4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy5Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownRecipePloy5
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

class IfdownShengchanjihua3Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownShengchanjihua3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

class IfdownShengchanjihua4Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownShengchanjihua4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua5Serializer(serializers.ModelSerializer):

    class Meta:
        model = IfdownShengchanjihua5
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