"""
auther :liwei
create_date:
updater:
update_time:
"""
import re

from django.contrib.auth.models import Permission
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator

from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from system.models import GroupExtension, User, Section, SystemConfig, ChildSystemInfo


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
        partten = r"^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{6,16}$"
        password = validated_data.get('password')
        if not re.search(partten, password):
            raise serializers.ValidationError("请输入6~16位长度包含字母和数字的密码")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

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