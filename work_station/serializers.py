# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/8/19
name: 
"""
from rest_framework import serializers

from mes.conf import COMMON_READ_ONLY_FIELDS
from work_station.models import *


# 新增万龙需求表的序列化器
# class IfdownRecipeWeigh1Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh1
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh2Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh2
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh3Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh3
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh4Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh4
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh5Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh5
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh6Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh6
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh7Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh7
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh8Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh8
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh9Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh9
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh10Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh10
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh11Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh11
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh12Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh12
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh13Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh13
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh14Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh14
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeWeigh15Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeWeigh15
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe1Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe1
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe2Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe2
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe3Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe3
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe4Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe4
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe5Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe5
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe6Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe6
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe7Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe7
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe8Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe8
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe9Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe9
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe10Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe10
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe11Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe11
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe12Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe12
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe13Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe13
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe14Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe14
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownPmtRecipe15Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownPmtRecipe15
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
#
#
# ###############################################################################################################
#
#
# class IfdownRecipeMix1Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix1
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix2Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix2
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix3Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix3
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix4Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix4
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix5Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix5
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix6Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix6
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix7Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix7
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix8Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix8
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix9Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix9
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix10Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix10
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix11Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix11
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix12Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix12
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix13Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix13
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix14Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix14
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownRecipeMix15Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownRecipeMix15
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# ####################################################################################################################
#
#
#
# class IfdownShengchanjihua1Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua1
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua2Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua2
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua3Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua3
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua4Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua4
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua5Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua5
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua6Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua6
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua7Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua7
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua8Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua8
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua9Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua9
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua10Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua10
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua11Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua11
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua12Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua12
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua13Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua13
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua14Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua14
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfdownShengchanjihua15Serializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfdownShengchanjihua15
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# ###############################################################################################################
#
#
# class IfupMachineStatusSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfupMachineStatus
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfupReportBasisSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfupReportBasis
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfupReportCurveSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfupReportCurve
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfupReportMixSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfupReportMix
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
#
#
# class IfupReportWeightSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = IfupReportWeight
#         fields = "__all__"
#         read_only_fields = COMMON_READ_ONLY_FIELDS
