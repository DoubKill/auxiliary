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
class IfdownRecipeWeigh1Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh1
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh2Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh2
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh3Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh3
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh4Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh4
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh5Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh5
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh6Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh6
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeWeigh15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeWeigh15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


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


class IfdownPmtRecipe7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownPmtRecipe15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownPmtRecipe15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


##############################################################################################################


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


class IfdownRecipeCb6Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb6
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeCb15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeCb15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


###############################################################################################################


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


class IfdownRecipeMix6Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix6
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeMix15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeMix15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


####################################################################################################################


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


class IfdownRecipeOil16Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil16
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil17Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil17
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil18Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil18
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil19Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil19
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil110Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil110
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil111Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil111
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil112Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil112
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil113Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil113
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil114Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil114
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipeOil115Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipeOil115
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


###########################################################################################################


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


class IfdownRecipePloy6Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy6
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownRecipePloy15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownRecipePloy15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


#############################################################################


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


class IfdownShengchanjihua6Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua6
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua7Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua7
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua8Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua8
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua9Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua9
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua10Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua10
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua11Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua11
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua12Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua12
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua13Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua13
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua14Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua14
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class IfdownShengchanjihua15Serializer(serializers.ModelSerializer):
    class Meta:
        model = IfdownShengchanjihua15
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


###############################################################################################################


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
