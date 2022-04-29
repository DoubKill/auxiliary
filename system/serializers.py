"""
auther :liwei
create_date:
updater:
update_time:
"""
import re

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from plan.models import ProductClassesPlan, ProductDayPlan
from recipe.models import ProductBatching, Material, ProductBatchingDetail
from system.models import GroupExtension, User, Section, SystemConfig, ChildSystemInfo, InterfaceOperationLog


class PermissionSerializer(BaseModelSerializer):
    class Meta:
        model = Permission
        fields = ("id", "codename", "name",)


class UserUpdateSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    num = serializers.CharField(required=False, validators=[
        UniqueValidator(queryset=User.objects.all(),
                        message='该用户工号已存在'),
    ])

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def update(self, instance, validated_data):
        validated_data['password'] = make_password(validated_data['password']) if validated_data.get(
            'password') else instance.password
        return super(UserUpdateSerializer, self).update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        # read_only_fields = COMMON_READ_ONLY_FIELDS


class UserSerializer(BaseModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    def create(self, validated_data):
        # partten = r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{3,16}$"
        password = validated_data.get('password')
        # if not re.search(partten, password):
        #     raise serializers.ValidationError("请输入3~16位长度包含字母和数字的密码")
        validated_data['created_user'] = self.context['request'].user
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_username(self, value):
        if len(value) > 64:
            raise ValidationError("用户名过长")
        if not re.search(r'^[a-zA-Z0-9\u4e00-\u9fa5]+$', value):
            raise serializers.ValidationError("用户名中包含非法字符")
        return value

    class Meta:
        model = User
        fields = '__all__'
        # read_only_fields = COMMON_READ_ONLY_FIELDS


class GroupUserSerializer(BaseModelSerializer):
    id = serializers.IntegerField()
    username = serializers.CharField(required=False)
    password = serializers.CharField(required=False)
    num = serializers.CharField(required=False)

    def to_representation(self, instance):
        instance = super().to_representation(instance)
        instance.pop('password')
        return instance

    class Meta:
        model = User
        fields = '__all__'


class GroupExtensionSerializer(BaseModelSerializer):
    """角色组扩展序列化器"""
    user_set = UserUpdateSerializer(read_only=True, many=True)

    def create(self, validated_data):
        validated_data['created_user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['last_updated_user'] = self.context['request'].user
        return super().update(instance, validated_data)

    class Meta:
        model = GroupExtension
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS

    def to_representation(self, instance):
        return super().to_representation(instance)


class GroupExtensionUpdateSerializer(BaseModelSerializer):
    """更新角色组用户序列化器"""

    class Meta:
        model = GroupExtension
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class GroupUserUpdateSerializer(BaseModelSerializer):
    """更新角色组用户序列化器"""
    user_set = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), write_only=True,
                                                  help_text="""{"user_set":[<user_id>, ……]}""")

    def update(self, instance, validated_data):
        user_ids = validated_data['user_set']
        instance.user_set.remove(*instance.user_set.all())
        instance.user_set.add(*user_ids)
        instance.save()
        return super().update(instance, validated_data)

    class Meta:
        model = GroupExtension
        fields = ('id', 'user_set')


class SectionSerializer(BaseModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class SystemConfigSerializer(BaseModelSerializer):
    class Meta:
        model = SystemConfig
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ChildSystemInfoSerializer(BaseModelSerializer):
    class Meta:
        model = ChildSystemInfo
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class InterfaceOperationLogSerializer(BaseModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = InterfaceOperationLog
        exclude = ('reasons',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


import logging
from django.conf import settings
import requests

logger = logging.getLogger('sync_log')


class BaseInterface(object):
    endpoint = settings.MES_URL

    class Backend:
        path = ""

    def request(self):
        if not self.Backend.path:
            raise NotImplementedError("未设置path")
        kwargs = getattr(self, 'data')
        logger.info(kwargs)
        try:
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                # "Authorization": kwargs['context']

            }
            res = requests.post(self.endpoint + self.Backend.path, headers=headers, json=kwargs)
        except Exception as err:
            logger.error(err)
            raise Exception('MES服务错误')
        logger.info(res.text)
        if res.status_code != 201:
            raise Exception(res.text)


class ProductBatchingDetailSyncInterface(serializers.ModelSerializer):
    material = serializers.CharField(source='material.material_no')

    class Meta:
        model = ProductBatchingDetail
        fields = ('product_batching', 'sn', 'material', 'actual_weight', 'standard_error', 'auto_flag', 'type')


class ProductBatchingSyncInterface(serializers.ModelSerializer):
    batching_details = ProductBatchingDetailSyncInterface(many=True)

    class Meta:
        model = ProductBatching
        fields = (
            'factory', 'site', 'product_info', 'precept', 'stage_product_batch_no', 'dev_type', 'stage', 'versions',
            'used_type', 'batching_weight', 'manual_material_weight', 'auto_material_weight', 'volume', 'submit_user',
            'submit_time', 'reject_user', 'reject_time', 'used_user', 'used_time', 'obsolete_user', 'obsolete_time',
            'production_time_interval',
            'equip', 'batching_type', 'batching_details')


class ProductDayPlanSyncInterface(serializers.ModelSerializer):
    product_batching = serializers.CharField(source='product_batching.stage_product_batch_no')

    class Meta:
        model = ProductDayPlan
        fields = ('equip', 'product_batching', 'plan_schedule')


class ProductClassesPlanSyncInterface(serializers.ModelSerializer, BaseInterface):
    """计划同步序列化器"""

    equip = serializers.CharField(source='equip.equip_no')
    work_schedule_plan = serializers.CharField(source='work_schedule_plan.work_schedule_plan_no')
    product_batching = ProductBatchingSyncInterface(read_only=True)
    product_day_plan = ProductDayPlanSyncInterface(read_only=True)

    class Backend:
        path = 'api/v1/system/plan-receive/'

    class Meta:
        model = ProductClassesPlan
        fields = ('product_day_plan',
                  'sn', 'plan_trains', 'time', 'weight', 'unit', 'work_schedule_plan',
                  'plan_classes_uid', 'note', 'equip',
                  'product_batching')


class MaterialSyncInterface(serializers.ModelSerializer, BaseInterface):
    """原材料同步序列化器"""

    material_type = serializers.CharField(source='material_type.global_no')
    package_unit = serializers.CharField(source='package_unit.global_no', read_only=True, default=0)

    class Backend:
        path = 'api/v1/system/material-receive/'

    class Meta:
        model = Material
        fields = ('material_no', 'material_name', 'for_short', 'material_type', 'package_unit', 'use_flag')
