import copy

from django.db.models import Q
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
    batching_details = serializers.DictField(write_only=True)
    weight_details = serializers.DictField(write_only=True)

    def get_material(self, material_name):
        try:
            material = Material.objects.get(material_name=material_name, delete_flag=False)
        except Material.DoesNotExist:
            raise serializers.ValidationError('原材料{}不存在'.format(material_name))
        return material

    def handle_xl(self, s_batching_detail, s_weight_detail, xl, type):
        xl_flag = []
        next_sn = 1
        c_o_data, keyword = [s_batching_detail['C'], 'C'] if type == 2 else [s_batching_detail['O'], 'O']
        for index, c in enumerate(c_o_data):
            mode = c.pop('feeding_mode')
            xl_data = {'material': xl, 'actual_weight': 0, 'standard_error': 0, 'type': type, 'auto_flag': 0, 'sn': next_sn}
            if index == 0:
                xl_flag.append(mode)
                s_batching_detail['P'].append(c)
                next_sn += 1
                # 判断是否存在走罐的化工原料
                for c_xl_tanks in s_weight_detail:
                    c_xl_tank = c_xl_tanks.pop('c_xl_tank', [])
                    if c_xl_tank:
                        for c_material in c_xl_tank:
                            tr_material = self.get_material(c_material.pop('material_name'))
                            c_material.update({'material': tr_material, 'type': 2, 'sn': next_sn, 'auto_flag': 0, 'standard_error': 0.2})
                            s_batching_detail['P'].append(c_material)
                            next_sn += 1
                if len(c_o_data) == 1:
                    xl_data['sn'] = next_sn
                    s_batching_detail['P'].append(xl_data)
                continue
            if mode == keyword:
                s_batching_detail['P'].append(xl_data)
                next_sn += 1
                c['sn'] = next_sn
                s_batching_detail['P'].append(c)
                next_sn += 1
                xl_flag += ['卸料', mode]
                if index == len(c_o_data) - 1:
                    xl_flag += ['卸料']
                    new_xl_data = copy.deepcopy(xl_data)
                    new_xl_data['sn'] = next_sn
                    s_batching_detail['P'].append(new_xl_data)
            else:
                c['sn'] = next_sn
                s_batching_detail['P'].append(c)
                next_sn += 1
                xl_flag += [mode]
                if index == len(c_o_data) - 1:
                    xl_flag += ['卸料']
                    new_xl_data = copy.deepcopy(xl_data)
                    new_xl_data['sn'] = next_sn
                    s_batching_detail['P'].append(new_xl_data)

    def validate(self, attrs):
        weight_details = attrs.pop('weight_details', None)
        batching_details = attrs.pop('batching_details', None)
        equip_no_list = batching_details.keys() if batching_details else weight_details.keys()
        dev_type = attrs.get('dev_type')
        try:
            dev_type = EquipCategoryAttribute.objects.get(category_no=dev_type)
        except EquipCategoryAttribute.DoesNotExist:
            raise serializers.ValidationError('上辅机机型{}不存在'.format(attrs.get('dev_type')))
        except Exception as e:
            raise e
        handle_batching_details = {}
        for equip_no in equip_no_list:
            s_batching_detail = batching_details.get(equip_no)
            s_weight_detail = weight_details.get(equip_no, [])
            p_sn = [i['sn'] for i in s_batching_detail['P']]
            c_sn = [i['sn'] for i in s_batching_detail['C']]
            o_sn = [i['sn'] for i in s_batching_detail['O']]
            # 更新 material
            for i in s_batching_detail['P'] + s_batching_detail['C'] + s_batching_detail['O']:
                material_name = i.pop('material_name')
                material = self.get_material(material_name)
                update_data = {'material': material, 'auto_flag': 0}
                i.update(**update_data)
                continue
            if c_sn:
                c_xl = Material.objects.filter(material_name='卸料', material_type__global_name='炭黑').first()
                if c_xl:
                    # 走罐化工原料与炭黑增加卸料
                    self.handle_xl(s_batching_detail, s_weight_detail, c_xl, type=2)
            if o_sn:
                o_xl = Material.objects.filter(material_name='卸料', material_type__global_name='油料').first()
                if o_xl:
                    # 油料增加卸料
                    self.handle_xl(s_batching_detail, s_weight_detail, o_xl, type=3)
            if p_sn:
                n_sn = max(p_sn) + 1
            else:
                n_sn = 1
            for weight_detail in s_weight_detail:
                # 料包总量是0不加入胶料区域
                if weight_detail['actual_weight'] == 0:
                    continue
                try:
                    xl_instance = self.get_material(weight_detail['material_name'])
                    add_data = {'material': xl_instance, 'actual_weight': weight_detail['actual_weight'],
                                'standard_error': weight_detail['standard_error'], 'type': 1, 'auto_flag': 0,
                                'sn': n_sn}
                    s_batching_detail['P'].append(add_data)
                    n_sn += 1
                except Exception as e:
                    raise e
            handle_batching_details[equip_no] = s_batching_detail['P']
        attrs.update({'dev_type': dev_type, 'batching_details': handle_batching_details})
        return attrs

    @atomic()
    def create(self, validated_data):
        special_recipe = False
        batching_details = validated_data.pop('batching_details')
        dev_type, product_no, batching_weight = validated_data['dev_type'], validated_data['stage_product_batch_no'].split('_NEW')[0], validated_data['batching_weight']
        try:
            # 正常胶料拆分
            init_site, init_stage, init_product_info, init_version = product_no.split('-')
        except:
            # 特殊胶料
            special_recipe = True
            init_site = init_stage = init_product_info = init_version = None
        batching_detail_list = []
        # 获取机台配方
        equip_recipes = ProductBatching.objects.exclude(used_type=6).filter(batching_type=1, dev_type=dev_type,
                                                                            stage_product_batch_no=product_no)
        for equip_no, details in batching_details.items():
            now_recipe = equip_recipes.filter(equip__equip_no=equip_no).first()
            if not now_recipe:  # 不存在机台配方则新增
                if not special_recipe:
                    factory = GlobalCode.objects.filter(global_type__type_name='产地', global_name='安吉').first()
                    site = GlobalCode.objects.filter(global_type__type_name='SITE', global_name=init_site).first()
                    stage = GlobalCode.objects.filter(global_type__type_name='胶料段次', global_name=init_stage).first()
                    product_info = ProductInfo.objects.filter(product_name=init_product_info).first()
                else:
                    factory = site = stage = product_info = None
                equip = Equip.objects.filter(equip_no=equip_no).first()
                create_recipe = {'factory': factory, 'stage_product_batch_no': product_no, 'dev_type': dev_type,
                                 'batching_weight': batching_weight, 'site': site, 'stage': stage, 'equip': equip,
                                 'product_info': product_info, 'versions': product_no.split('-')[-1]}
                now_recipe = ProductBatching.objects.create(**create_recipe)
            else:
                # 删除之前确定掺料和待处理料的顺序
                other_material = now_recipe.batching_details.filter(Q(material__material_name__icontains='待处理料') |
                                                                    Q(material__material_name__icontains='掺料'),
                                                                    delete_flag=False, type=1).last()
                if other_material:
                    other_material_info = {'type': 1, 'actual_weight': other_material.actual_weight, 'auto_flag': 0,
                                           'standard_error': other_material.standard_error,
                                           'material': other_material.material}
                    xl = now_recipe.batching_details.filter(delete_flag=False, type=1, material__material_name__in=['细料', '硫磺']).last()
                    new_details = []
                    if xl:
                        point = 0
                        for detail in details:
                            if detail['type'] != 1:
                                new_details.append(detail)
                                continue
                            if detail['material'].material_name in ['细料', '硫磺']:
                                point = detail['sn']
                                if xl.sn > other_material.sn:  # 掺料或待处理料在料包前
                                    other_material_info['sn'] = point
                                    detail['sn'] = point + 1
                                    new_details += [other_material_info, detail]
                                else:
                                    other_material_info['sn'] = point + 1
                                    new_details += [detail, other_material_info]
                            else:
                                if point != 0:
                                    detail['sn'] = detail['sn'] + 1
                                new_details.append(detail)
                        details = new_details
                    else:
                        other_material_info['sn'] = max([i['sn'] for i in details if i['type'] == 1]) + 1
                        details.append(other_material_info)
                now_recipe.batching_details.all().delete()
                now_recipe.batching_weight = validated_data['batching_weight']
                now_recipe.used_type = 1
                now_recipe.save()
            for detail in details:
                tank = None
                if detail['type'] == 2:
                    tank = MaterialTankStatus.objects.filter(equip_no=now_recipe.equip.equip_no,
                                                             tank_type=1,
                                                             material_no=detail['material'].material_no).first()
                elif detail['type'] == 3:
                    tank = MaterialTankStatus.objects.filter(equip_no=now_recipe.equip.equip_no,
                                                             tank_type=2,
                                                             material_no=detail['material'].material_no).first()
                if tank:
                    detail['tank_no'] = tank.tank_no
                detail['product_batching'] = now_recipe
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