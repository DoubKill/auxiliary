from django.db.transaction import atomic

from basics.models import GlobalCode, GlobalCodeType, WorkSchedule, ClassesDetail, EquipCategoryAttribute, Equip, \
    PlanSchedule, WorkSchedulePlan
from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from rest_framework import serializers

from recipe.models import Material


class GlobalCodeReceiveSerializer(BaseModelSerializer):
    global_type__type_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        global_type = attrs.pop('global_type__type_no')
        try:
            global_type = GlobalCodeType.objects.get(type_no=global_type)
        except GlobalCodeType.DoesNotExist:
            raise serializers.ValidationError('类型编号{}不存在'.format(attrs.get('global_type')))
        attrs['global_type'] = global_type
        return attrs

    @atomic()
    def create(self, validated_data):
        global_no = validated_data['global_no']
        instance = GlobalCode.objects.filter(global_no=global_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = GlobalCode
        fields = ('global_type__type_no', 'global_no', 'global_name', 'description', 'use_flag')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'global_no': {'validators': []}}


class WorkScheduleReceiveSerializer(BaseModelSerializer):
    """倒班管理"""

    @atomic()
    def create(self, validated_data):
        schedule_no = validated_data['schedule_no']
        instance = WorkSchedule.objects.filter(schedule_no=schedule_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = WorkSchedule
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'schedule_no': {'validators': []}}


class ClassesDetailReceiveSerializer(BaseModelSerializer):
    """倒班条目"""
    work_schedule__schedule_no = serializers.CharField(write_only=True)
    classes__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        work_schedule = attrs.pop('work_schedule__schedule_no')
        classes = attrs.pop('classes__global_no')
        try:
            work_schedule = WorkSchedule.objects.get(schedule_no=work_schedule)
            classes = GlobalCode.objects.get(global_no=classes)
        except WorkSchedule.DoesNotExist:
            raise serializers.ValidationError('倒班编号{}不存在'.format(attrs.get('work_schedule')))
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('班次{}不存在'.format(attrs.get('classes')))
        attrs['work_schedule'] = work_schedule
        attrs['classes'] = classes
        return attrs

    @atomic()
    def create(self, validated_data):
        work_schedule = validated_data['work_schedule']
        classes = validated_data['classes']
        instance = ClassesDetail.objects.filter(work_schedule=work_schedule, classes=classes)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = ClassesDetail
        fields = ('work_schedule__schedule_no', 'classes__global_no', 'description', 'start_time', 'end_time')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class EquipCategoryAttributeSerializer(BaseModelSerializer):
    """设备种类属性"""
    equip_type__global_no = serializers.CharField(write_only=True)
    process__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        equip_type = attrs.pop('equip_type__global_no')
        process = attrs.pop('process__global_no')
        try:
            equip_type = GlobalCode.objects.get(global_no=equip_type)
            process = GlobalCode.objects.get(global_no=process)
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('设备类型{}不存在'.format(attrs.get('equip_type')))
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('工序{}不存在'.format(attrs.get('process')))
        attrs['equip_type'] = equip_type
        attrs['process'] = process
        return attrs

    @atomic()
    def create(self, validated_data):
        category_no = validated_data['category_no']
        instance = EquipCategoryAttribute.objects.filter(category_no=category_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = EquipCategoryAttribute
        fields = (
            'equip_type__global_no', 'category_no', 'category_name', 'volume', 'description', 'process__global_no',
            'use_flag')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'category_no': {'validators': []}}


class EquipSerializer(BaseModelSerializer):
    """设备"""
    category__category_no = serializers.CharField(write_only=True)
    equip_level__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        category = attrs.pop('category__category_no')
        equip_level = attrs.pop('equip_level__global_no')
        try:
            category = EquipCategoryAttribute.objects.get(category_no=category)
            equip_level = GlobalCode.objects.get(global_no=equip_level)
        except EquipCategoryAttribute.DoesNotExist:
            raise serializers.ValidationError('设备种类属性{}不存在'.format(attrs.get('category')))
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('层级{}不存在'.format(attrs.get('equip_level')))
        attrs['category'] = category
        attrs['equip_level'] = equip_level
        return attrs

    @atomic()
    def create(self, validated_data):
        equip_no = validated_data['equip_no']
        instance = Equip.objects.filter(equip_no=equip_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = Equip
        fields = ('category__category_no', 'parent', 'equip_no', 'equip_name', 'use_flag', 'description', 'count_flag',
                  'equip_level__global_no')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'equip_no': {'validators': []}}


class PlanScheduleSerializer(BaseModelSerializer):
    """排班管理"""
    work_schedule__schedule_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        work_schedule = attrs.pop('work_schedule__schedule_no')
        try:
            work_schedule = WorkSchedule.objects.get(schedule_no=work_schedule)
        except WorkSchedule.DoesNotExist:
            raise serializers.ValidationError('倒班id{}不存在'.format(attrs.get('work_schedule')))
        attrs['work_schedule'] = work_schedule
        return attrs

    @atomic()
    def create(self, validated_data):
        plan_schedule_no = validated_data['plan_schedule_no']
        instance = PlanSchedule.objects.filter(plan_schedule_no=plan_schedule_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = PlanSchedule
        fields = ('plan_schedule_no', 'day_time', 'work_schedule__schedule_no')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'plan_schedule_no': {'validators': []}}


class WorkSchedulePlanSerializer(BaseModelSerializer):
    """排班详情"""

    classes__global_no = serializers.CharField(write_only=True)
    plan_schedule__plan_schedule_no = serializers.CharField(write_only=True)
    group__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        classes = attrs.pop('classes__global_no')
        plan_schedule = attrs.pop('plan_schedule__plan_schedule_no')
        group = attrs.pop('group__global_no')
        try:
            classes = GlobalCode.objects.get(global_no=classes)
            plan_schedule = PlanSchedule.objects.get(plan_schedule_no=plan_schedule)
            group = GlobalCode.objects.get(global_no=group)
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('班次{}不存在'.format(attrs.get('classes')))
        except PlanSchedule.DoesNotExist:
            raise serializers.ValidationError('计划时间id{}不存在'.format(attrs.get('plan_schedule')))
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('班组id{}不存在'.format(attrs.get('group')))
        attrs['classes'] = classes
        attrs['plan_schedule'] = plan_schedule
        attrs['group'] = group
        return attrs

    @atomic()
    def create(self, validated_data):
        work_schedule_plan_no = validated_data['work_schedule_plan_no']
        instance = WorkSchedulePlan.objects.filter(work_schedule_plan_no=work_schedule_plan_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = WorkSchedulePlan
        fields = ('work_schedule_plan_no', 'classes__global_no', 'rest_flag', 'plan_schedule__plan_schedule_no',
                  'group__global_no', 'start_time', 'end_time')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'work_schedule_plan_no': {'validators': []}}


class MaterialSerializer(BaseModelSerializer):
    material_type__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        material_type = attrs.pop('material_type__global_no')
        try:
            material_type = GlobalCode.objects.get(global_no=material_type)
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('原材料类别{}不存在'.format(attrs.get('material_type')))
        attrs['material_type'] = material_type
        return attrs

    @atomic()
    def create(self, validated_data):
        material_no = validated_data['material_no']
        instance = Material.objects.filter(material_no=material_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = Material
        fields = ('material_no', 'material_name', 'for_short', 'material_type__global_no', 'use_flag')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'material_no': {'validators': []}}


class GlobalCodeTypeSerializer(BaseModelSerializer):

    @atomic()
    def create(self, validated_data):
        type_no = validated_data['type_no']
        instance = GlobalCodeType.objects.filter(type_no=type_no)
        if instance:
            instance.update(**validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = GlobalCodeType
        fields = ('type_no', 'type_name', 'description', 'use_flag')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'type_no': {'validators': []}}
