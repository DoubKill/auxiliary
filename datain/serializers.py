from django.db.transaction import atomic

from basics.models import GlobalCode, GlobalCodeType, WorkSchedule, ClassesDetail, EquipCategoryAttribute, Equip, \
    PlanSchedule, WorkSchedulePlan
from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from rest_framework import serializers

from production.models import MaterialTankStatus
from recipe.models import Material, ProductInfo, ProductBatchingDetail, ProductBatching, MaterialAttribute, \
    MaterialSupplier


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
        instance = GlobalCode.objects.filter(global_no=global_no).first()
        if instance:
            super().update(instance, validated_data)
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
    work_procedure__global_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        work_procedure_no = attrs.pop('work_procedure__global_no')
        try:
            work_procedure = GlobalCode.objects.get(global_no=work_procedure_no)
        except GlobalCode.DoesNotExist:
            raise serializers.ValidationError('工序{}不存在'.format(attrs.get('work_procedure')))
        attrs['work_procedure'] = work_procedure
        return attrs

    @atomic()
    def create(self, validated_data):
        schedule_no = validated_data['schedule_no']
        work_procedure = validated_data['work_procedure']
        instance = WorkSchedule.objects.filter(schedule_no=schedule_no, work_procedure=work_procedure).first()
        if instance:
            super().update(instance, validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = WorkSchedule
        fields = ("schedule_no", "schedule_name", "period", "description", "use_flag", "work_procedure__global_no")
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
        instance = ClassesDetail.objects.filter(work_schedule=work_schedule, classes=classes).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = EquipCategoryAttribute.objects.filter(category_no=category_no).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = Equip.objects.filter(equip_no=equip_no).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = PlanSchedule.objects.filter(plan_schedule_no=plan_schedule_no).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = WorkSchedulePlan.objects.filter(work_schedule_plan_no=work_schedule_plan_no).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = Material.objects.filter(material_no=material_no).first()
        if instance:
            super().update(instance, validated_data)
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
        instance = GlobalCodeType.objects.filter(type_no=type_no).first()
        if instance:
            super().update(instance, validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = GlobalCodeType
        fields = ('type_no', 'type_name', 'description', 'use_flag')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {'type_no': {'validators': []}}


class ProductInfoSerializer(BaseModelSerializer):

    @atomic()
    def create(self, validated_data):
        product_no = validated_data['product_no']
        instance = ProductInfo.objects.filter(product_no=product_no).first()
        if instance:
            super().update(instance, validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = ProductInfo
        fields = '__all__'
        extra_kwargs = {'product_no': {'validators': []}}


class ProductBatchingDetailSerializer2(serializers.ModelSerializer):
    material = serializers.CharField()

    def validate(self, attrs):
        try:
            material = Material.objects.get(material_no=attrs['material'])
        except Material.DoesNotExist:
            raise serializers.ValidationError('原材料{}不存在'.format(attrs['material']))
        attrs['material'] = material
        return attrs

    class Meta:
        model = ProductBatchingDetail
        fields = ('sn', 'material', 'actual_weight', 'standard_error', 'auto_flag', 'type')


class RecipeReceiveSerializer(serializers.ModelSerializer):
    dev_type = serializers.CharField()
    batching_details = ProductBatchingDetailSerializer2(many=True, write_only=True)
    weight_details = serializers.ListField(write_only=True)

    def validate(self, attrs):
        weight_details = attrs.pop('weight_details', None)
        batching_details = attrs['batching_details']
        p_sn = [i['sn'] for i in batching_details if i['type'] == 1]
        o_sn = [i['sn'] for i in batching_details if i['type'] == 3]
        c_sn = [i['sn'] for i in batching_details if i['type'] == 2]
        if o_sn:
            o_xl = Material.objects.filter(material_name='卸料', material_type__global_name='油料').first()
            if o_xl:
                attrs['batching_details'].append({'material': o_xl,
                                                  'actual_weight': 0,
                                                  'standard_error': 0,
                                                  'type': 3,
                                                  'auto_flag': 0,
                                                  'sn': max(o_sn) + 1
                                                  })
        if c_sn:
            c_xl = Material.objects.filter(material_name='卸料', material_type__global_name='炭黑').first()
            if c_xl:
                attrs['batching_details'].append({'material': c_xl,
                                                  'actual_weight': 0,
                                                  'standard_error': 0,
                                                  'type': 2,
                                                  'auto_flag': 0,
                                                  'sn': max(c_sn) + 1
                                                  })
        dev_type = attrs.get('dev_type')
        try:
            dev_type = EquipCategoryAttribute.objects.get(category_no=dev_type)
        except EquipCategoryAttribute.DoesNotExist:
            raise serializers.ValidationError('上辅机机型{}不存在'.format(attrs.get('dev_type')))
        except Exception as e:
            raise e
        material_type = GlobalCode.objects.filter(global_type__type_name='原材料类别',
                                                  global_name='料包').first()
        if material_type:
            if p_sn:
                sn = max(p_sn) + 1
            else:
                sn = 1
            for weight_detail in weight_details:
                try:
                    m, _ = Material.objects.get_or_create(
                        material_no=weight_detail['material'],
                        material_name=weight_detail['material'],
                        material_type=material_type)
                    attrs['batching_details'].append({'material': m,
                                                      'actual_weight': weight_detail['actual_weight'],
                                                      'standard_error': weight_detail['standard_error'],
                                                      'type': 1,
                                                      'auto_flag': 0,
                                                      'sn': sn
                                                      })
                    sn += 1
                except Exception as e:
                    raise e
        attrs['dev_type'] = dev_type
        return attrs

    @atomic()
    def create(self, validated_data):
        batching_details = validated_data.pop('batching_details')
        batching_detail_list = []
        for product_batching in ProductBatching.objects.exclude(used_type=6).filter(
                batching_type=1,
                dev_type=validated_data['dev_type'],
                stage_product_batch_no=validated_data['stage_product_batch_no']):
            product_batching.batching_details.all().delete()
            product_batching.batching_weight = validated_data['batching_weight']
            product_batching.used_type = 1
            product_batching.save()
            for detail in batching_details:
                tank = None
                if detail['type'] == 2:
                    tank = MaterialTankStatus.objects.filter(equip_no=product_batching.equip.equip_no,
                                                             tank_type=1,
                                                             material_no=detail['material'].material_no).first()
                elif detail['type'] == 3:
                    tank = MaterialTankStatus.objects.filter(equip_no=product_batching.equip.equip_no,
                                                             tank_type=2,
                                                             material_no=detail['material'].material_no).first()
                if tank:
                    detail['tank_no'] = tank.tank_no
                detail['product_batching'] = product_batching
                batching_detail_list.append(ProductBatchingDetail(**detail))
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        return validated_data

    class Meta:
        model = ProductBatching
        fields = ('dev_type', 'stage_product_batch_no', 'batching_details', 'weight_details', 'batching_weight')


class MaterialAttributeReceiveSerializer(serializers.ModelSerializer):
    material__material_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        material__material_no = attrs.pop('material__material_no')
        try:
            material = Material.objects.get(material_no=material__material_no)
        except Material.DoesNotExist:
            raise serializers.ValidationError('原材料{}不存在'.format(attrs.get('material__material_no')))
        attrs['material'] = material
        return attrs

    def create(self, validated_data):
        material = validated_data['material']
        instance = MaterialAttribute.objects.filter(material=material).first()
        if instance:
            super().update(instance, validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = MaterialAttribute
        fields = ('material__material_no', 'safety_inventory', 'period_of_validity', 'validity_unit')
        extra_kwargs = {'material': {'validators': []}}


class MaterialSupplierReceiveSerializer(serializers.ModelSerializer):
    material__material_no = serializers.CharField(write_only=True)

    def validate(self, attrs):
        material__material_no = attrs.pop('material__material_no')
        try:
            material = Material.objects.get(material_no=material__material_no)
        except Material.DoesNotExist:
            raise serializers.ValidationError('原材料{}不存在'.format(attrs.get('material__material_no')))
        attrs['material'] = material
        return attrs

    @atomic()
    def create(self, validated_data):
        supplier_no = validated_data['supplier_no']
        instance = MaterialSupplier.objects.filter(supplier_no=supplier_no).first()
        if instance:
            super().update(instance, validated_data)
        else:
            super().create(validated_data)
        return validated_data

    class Meta:
        model = MaterialSupplier
        fields = ('material__material_no', 'supplier_no', 'provenance', 'use_flag')
        extra_kwargs = {'supplier_no': {'validators': []}}