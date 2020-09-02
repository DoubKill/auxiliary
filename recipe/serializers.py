from datetime import datetime
import logging

from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from basics.models import GlobalCode, EquipCategoryAttribute, Equip
from mes.base_serializer import BaseModelSerializer
from recipe.models import Material, ProductInfo, ProductBatching, ProductBatchingDetail, \
    MaterialAttribute, ProductProcess, ProductProcessDetail
from mes.conf import COMMON_READ_ONLY_FIELDS

logger = logging.getLogger('api_log')


class MaterialSerializer(BaseModelSerializer):
    material_no = serializers.CharField(max_length=64, help_text='编码',
                                        validators=[UniqueValidator(queryset=Material.objects.filter(delete_flag=0),
                                                                    message='该原材料已存在')])
    material_type = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.filter(use_flag=0,
                                                                                          delete_flag=False),
                                                       help_text='原材料类型id',
                                                       error_messages={'does_not_exist': '该原材料类型已被弃用或删除，操作无效'})
    package_unit = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.filter(use_flag=0,
                                                                                         delete_flag=False),
                                                      help_text='包装单位id', required=False,
                                                      allow_null=True, allow_empty=True,
                                                      error_messages={'does_not_exist': '该包装单位类型已被弃用或删除，操作无效'})
    material_type_name = serializers.CharField(source='material_type.global_name', read_only=True)
    package_unit_name = serializers.CharField(source='package_unit.global_name', read_only=True)
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.CharField(source='last_updated_user.username', default=None, read_only=True)

    def update(self, instance, validated_data):
        validated_data['last_updated_user'] = self.context['request'].user
        return super().update(instance, validated_data)

    class Meta:
        model = Material
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialAttributeSerializer(BaseModelSerializer):
    material_no = serializers.CharField(source='Material.material_no', read_only=True)
    material_name = serializers.CharField(source='Material.material_name', read_only=True)

    class Meta:
        model = MaterialAttribute
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductInfoSerializer(BaseModelSerializer):
    update_username = serializers.CharField(source='last_updated_user.username', read_only=True)

    class Meta:
        model = ProductInfo
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductInfoCopySerializer(BaseModelSerializer):
    factory = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.filter(use_flag=0, delete_flag=False),
                                                 help_text='产地id')

    def validate(self, attrs):
        versions = attrs['versions']
        factory = attrs['factory']
        product_no = attrs['product_info_id'].product_no
        product_info = ProductInfo.objects.filter(factory=factory, product_no=product_no).order_by('-versions').first()
        if product_info:
            if product_info.versions >= versions:  # TODO 目前版本检测根据字符串做比较，后期搞清楚具体怎样填写版本号
                raise serializers.ValidationError('版本不得小于目前已有的版本')
        attrs['used_type'] = 1
        return attrs

    @atomic()
    def create(self, validated_data):
        base_product_info = validated_data.pop('product_info_id')
        validated_data['created_user'] = self.context['request'].user
        validated_data['recipe_weight'] = base_product_info.recipe_weight
        validated_data['product_no'] = base_product_info.product_no
        validated_data['product_name'] = base_product_info.product_name
        validated_data['precept'] = base_product_info.precept
        instance = super().create(validated_data)
        return instance

    class Meta:
        model = ProductInfo
        fields = '__all__'


class ProductBatchingDetailSerializer(BaseModelSerializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.filter(delete_flag=False, use_flag=1))
    material_type = serializers.CharField(source='material.material_type.global_name', read_only=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)

    class Meta:
        model = ProductBatchingDetail
        exclude = ('product_batching', )


class ProductBatchingListSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source='product_info.product_name', read_only=True)
    created_user_name = serializers.CharField(source='created_user.username', read_only=True)
    update_user_name = serializers.CharField(source='last_updated_user.username', read_only=True)
    stage_name = serializers.CharField(source="stage.global_name", read_only=True)
    site_name = serializers.CharField(source="site.global_name", read_only=True)
    dev_type_name = serializers.CharField(source='dev_type.category_name', default=None, read_only=True)
    equip_no = serializers.CharField(source='equip.equip_no', default=None, read_only=True)
    equip_name = serializers.CharField(source='equip.equip_name', default=None, read_only=True)
    sp_num = serializers.SerializerMethodField(read_only=True)

    @staticmethod
    def get_sp_num(obj):
        if obj.equip:
            process = ProductProcess.objects.filter(equip=obj.equip, product_batching=obj).first()
            if process:
                return process.sp_num
            return None
        return None

    class Meta:
        model = ProductBatching
        fields = '__all__'


class ProductBatchingCreateSerializer(BaseModelSerializer):
    stage = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.filter(use_flag=0, delete_flag=False),
                                               help_text='段次id')
    batching_details = ProductBatchingDetailSerializer(many=True, required=False,
                                                       help_text="""
                                                           [{"sn": 序号, "material":原材料id, "auto_flag": true,
                                                           "actual_weight":重量, "standard_error":误差值}]""")

    def validate(self, attrs):
        stage_product_batch_no = attrs['stage_product_batch_no']
        equip = attrs['equip']
        if ProductBatching.objects.filter(stage_product_batch_no=stage_product_batch_no, equip=equip).exists():
            raise serializers.ValidationError('已存在相同机台的配方，请修改后重试！')
        return attrs

    @atomic()
    def create(self, validated_data):
        batching_details = validated_data.pop('batching_details', None)
        validated_data['dev_type'] = validated_data['equip'].category
        instance = super().create(validated_data)
        batching_weight = manual_material_weight = auto_material_weight = 0
        if batching_details:
            batching_detail_list = [None] * len(batching_details)
            for i, detail in enumerate(batching_details):
                auto_flag = detail.get('detail')
                actual_weight = detail.get('actual_weight', 0)
                if auto_flag == 1:
                    auto_material_weight += actual_weight
                elif auto_flag == 2:
                    manual_material_weight += actual_weight
                batching_weight += actual_weight
                detail['product_batching'] = instance
                batching_detail_list[i] = ProductBatchingDetail(**detail)
            ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        instance.batching_weight = batching_weight
        instance.manual_material_weight = manual_material_weight
        instance.auto_material_weight = auto_material_weight
        instance.save()
        try:
            material_type = GlobalCode.objects.filter(global_type__type_name='原材料类别',
                                                      global_name=instance.stage.global_name).first()
            Material.objects.get_or_create(
                material_no=instance.stage_product_batch_no,
                material_name=instance.stage_product_batch_no,
                material_type=material_type
            )
        except Exception as e:
            logger.error(e)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('factory', 'site', 'product_info', 'precept', 'stage_product_batch_no',
                  'stage', 'versions', 'batching_details', 'equip', 'id', 'dev_type')
        extra_kwargs = {'equip': {'required': True}}


class ProductBatchingRetrieveSerializer(ProductBatchingListSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, required=False,
                                                       help_text="""
                                                       [{"sn": 序号, "material":原材料id, 
                                                       "actual_weight":重量, "error_range":误差值}]""")

    class Meta:
        model = ProductBatching
        fields = '__all__'


class ProductBatchingUpdateSerializer(ProductBatchingRetrieveSerializer):

    @atomic()
    def update(self, instance, validated_data):
        if instance.used_type != 1:
            raise serializers.ValidationError('只有编辑状态的配方才可修改')
        batching_details = validated_data.pop('batching_details', None)
        instance = super().update(instance, validated_data)
        batching_weight = manual_material_weight = auto_material_weight = 0
        if batching_details is not None:
            instance.batching_details.all().delete()
            batching_detail_list = [None] * len(batching_details)
            for i, detail in enumerate(batching_details):
                actual_weight = detail.get('actual_weight', 0)
                auto_flag = detail.get('detail')
                if auto_flag == 1:
                    auto_material_weight += actual_weight
                elif auto_flag == 2:
                    manual_material_weight += actual_weight
                batching_weight += actual_weight
                detail['product_batching'] = instance
                batching_detail_list[i] = ProductBatchingDetail(**detail)
            ProductBatchingDetail.objects.bulk_create(batching_detail_list)
            instance.batching_weight = batching_weight
            instance.manual_material_weight = manual_material_weight
            instance.auto_material_weight = auto_material_weight
            instance.save()
        return instance

    class Meta:
        model = ProductBatching
        fields = ('id', 'batching_details', 'dev_type', 'production_time_interval', 'equip')


class ProductBatchingPartialUpdateSerializer(BaseModelSerializer):
    pass_flag = serializers.BooleanField(help_text='通过标志，1：通过, 0:驳回', write_only=True)

    def update(self, instance, validated_data):
        pass_flag = validated_data['pass_flag']
        if pass_flag:
            if instance.used_type == 1:  # 审核通过
                instance.used_type = 2
            elif instance.used_type == 2:  # 审核通过
                instance.used_type = 3
            elif instance.used_type == 3:  # 启用
                # 废弃旧版本
                ProductBatching.objects.filter(used_type=4,
                                               site=instance.site,
                                               product_info=instance.product_info,
                                               factory=instance.factory,
                                               stage=instance.stage
                                               ).update(used_type=6, used_time=datetime.now())
                instance.used_type = 4
                instance.used_user = self.context['request'].user
                instance.used_time = datetime.now()
        else:
            if instance.used_type == 4:  # 弃用
                instance.obsolete_user = self.context['request'].user
                instance.used_type = 6
                instance.obsolete_time = datetime.now()
            else:  # 驳回
                instance.used_type = 5
        instance.last_updated_user = self.context['request'].user
        instance.save()
        return instance

    class Meta:
        model = ProductBatching
        fields = ('id', 'pass_flag')


class ProductProcessDetailSerializer(BaseModelSerializer):
    condition_name = serializers.CharField(source='condition.condition', read_only=True)
    action_name = serializers.CharField(source='action.action', read_only=True)

    class Meta:
        model = ProductProcessDetail
        exclude = ('product_process', )
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProcessDetailSerializer(BaseModelSerializer):

    class Meta:
        model = ProductProcessDetail
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductProcessSerializer(BaseModelSerializer):
    process_details = ProductProcessDetailSerializer(many=True, required=False, help_text="""
                                                                                        [{"sn":'序号',
                                                                                        "temperature":'温度',
                                                                                        "rpm":'转速',
                                                                                        "energy": '能量',
                                                                                        "power": '功率',
                                                                                        "pressure" : '压力',
                                                                                        "condition": '条件id',
                                                                                        "time" :'时间(分钟)',
                                                                                        "action":'基本动作id',
                                                                                        "time_unit":'时间单位'}]""")

    @atomic()
    def create(self, validated_data):
        product_batching = validated_data['product_batching']
        if not product_batching.equip:
            # 给配方加上机台
            product_batching.equip = validated_data['equip']
            product_batching.save()
        validated_data['created_user'] = self.context['request'].user
        process_details = validated_data.pop('process_details', None)
        instance = super().create(validated_data)
        batching_detail_list = []
        for detail in process_details:
            detail['product_process'] = instance
            batching_detail_list.append(ProductProcessDetail(**detail))
        ProductProcessDetail.objects.bulk_create(batching_detail_list)
        return instance

    @atomic()
    def update(self, instance, validated_data):
        process_details = validated_data.pop('process_details', None)
        instance = super().update(instance, validated_data)
        if process_details:
            instance.process_details.all().delete()
            batching_detail_list = []
            for detail in process_details:
                detail['product_process'] = instance
                batching_detail_list.append(ProductProcessDetail(**detail))
            ProductProcessDetail.objects.bulk_create(batching_detail_list)
        return instance

    class Meta:
        model = ProductProcess
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
        validators = [
                    UniqueTogetherValidator(
                        queryset=model.objects.filter(delete_flag=False),
                        fields=('equip', 'product_batching'),
                        message="该机台已绑定相同配方，请修改后重试！"
                    )
                ]


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
        fields = ('sn', 'material', 'actual_weight', 'standard_error', 'auto_flag')


class RecipeReceiveSerializer(serializers.ModelSerializer):
    factory = serializers.CharField()
    site = serializers.CharField()
    product_info = serializers.CharField()
    dev_type = serializers.CharField(allow_blank=True, allow_null=True)
    stage = serializers.CharField()
    equip = serializers.CharField(allow_blank=True, allow_null=True)
    batching_details = ProductBatchingDetailSerializer2(many=True)

    def validate(self, attrs):
        stage_product_batch_no = attrs['stage_product_batch_no']
        dev_type = attrs.get('dev_type')
        equip = attrs.get('equip')
        if ProductBatching.objects.filter(stage_product_batch_no=stage_product_batch_no):
            raise serializers.ValidationError('该配方已存在， 请重试！')
        try:
            if dev_type:
                dev_type = EquipCategoryAttribute.objects.get(category_no=dev_type)
            if equip:
                equip = Equip.objects.get(equip_no=equip)
            factory = GlobalCode.objects.get(global_no=attrs['factory'])
            site = GlobalCode.objects.get(global_no=attrs['site'])
            product_info = ProductInfo.objects.get(product_no=attrs['product_info'])
            stage = GlobalCode.objects.get(global_no=attrs['stage'])
        except Equip.DoesNotExist:
            raise serializers.ValidationError('上辅机机台{}不存在'.format(attrs.get('equip')))
        except EquipCategoryAttribute.DoesNotExist:
            raise serializers.ValidationError('上辅机机型{}不存在'.format(attrs.get('dev_type')))
        except GlobalCode.DoesNotExist as e:
            raise serializers.ValidationError('公共代码{}不存在'.format(e))
        except ProductInfo.DoesNotExist:
            raise serializers.ValidationError('胶料代码{}不存在'.format(attrs['product_info']))
        attrs['dev_type'] = dev_type
        attrs['factory'] = factory
        attrs['equip'] = equip
        attrs['site'] = site
        attrs['product_info'] = product_info
        attrs['stage'] = stage
        return attrs

    @atomic()
    def create(self, validated_data):
        batching_details = validated_data.pop('batching_details')
        instance = super().create(validated_data)
        batching_detail_list = [None] * len(batching_details)
        for i, detail in enumerate(batching_details):
            detail['product_batching'] = instance
            batching_detail_list[i] = ProductBatchingDetail(**detail)
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('created_date', 'factory', 'site', 'product_info',
                  'dev_type', 'stage', 'equip', 'used_time', 'precept', 'stage_product_batch_no',
                  'versions', 'used_type', 'batching_weight', 'manual_material_weight',
                  'auto_material_weight', 'production_time_interval', 'batching_details')


class ProductBatchingSerializer(serializers.ModelSerializer):
    product_batching = serializers.PrimaryKeyRelatedField(queryset=ProductBatching.objects.all(), help_text='配方id',
                                                          write_only=True)

    @atomic()
    def create(self, validated_data):
        base_product_batching = validated_data['product_batching']
        equip = validated_data['equip']

        if ProductBatching.objects.filter(stage_product_batch_no=base_product_batching.stage_product_batch_no,
                                          equip=equip).exists():
            raise serializers.ValidationError('已存在相同机台的配方，请修改后重试！')

        product_batching_dict = ProductBatching.objects.filter(
            id=base_product_batching.id).values('factory_id', 'site_id', 'product_info_id', 'precept',
                                                'stage_product_batch_no', 'dev_type_id', 'stage_id', 'versions',
                                                'used_type', 'batching_weight', 'manual_material_weight',
                                                'auto_material_weight')[0]
        batching_details = ProductBatchingDetail.objects.filter(
            product_batching=base_product_batching).values('sn', 'material_id', 'actual_weight',
                                                           'standard_error', 'auto_flag')

        product_batching_dict['equip'] = equip
        product_batching_dict['used_type'] = 1
        # 复制配方和配方详情
        product_batching = ProductBatching.objects.create(**product_batching_dict)
        batching_detail_list = [None] * len(batching_details)
        for i, batching_detail in enumerate(batching_details):
            batching_detail['product_batching'] = product_batching
            batching_detail_list[i] = ProductBatchingDetail(**batching_detail)
        ProductBatchingDetail.objects.bulk_create(batching_detail_list)

        # 复制步序和步序详情
        if base_product_batching.equip:
            # 有机台才有步序信息
            base_process = ProductProcess.objects.filter(product_batching=base_product_batching,
                                                         equip=base_product_batching.equip
                                                         )
            if base_process:
                base_process_dict = base_process.values('equip_code', 'reuse_time', 'mini_time', 'max_time',
                                                        'mini_temp', 'max_temp', 'over_time', 'over_temp',
                                                        'reuse_flag', 'zz_temp', 'xlm_temp', 'cb_temp',
                                                        'temp_use_flag', 'use_flag', 'batching_error',
                                                        'sp_num')[0]
                process_details = ProductProcessDetail.objects.filter(
                    product_process=base_process.first()).values('sn', 'temperature', 'rpm', 'energy', 'power',
                                                                 'pressure', 'condition_id', 'time', 'action_id',
                                                                 'time_unit')
                base_process_dict['equip'] = equip
                base_process_dict['product_batching'] = product_batching
                process = ProductProcess.objects.create(**base_process_dict)
                process_detail_list = [None] * len(process_details)
                for i, process_details in enumerate(process_details):
                    process_details['product_process'] = process
                    process_detail_list[i] = ProductProcessDetail(**process_details)
                ProductProcessDetail.objects.bulk_create(process_detail_list)
        return validated_data

    class Meta:
        model = ProductBatching
        fields = ('product_batching', 'equip')
        extra_kwargs = {'equip': {'required': True}}