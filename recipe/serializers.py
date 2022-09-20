import json
import operator
from datetime import datetime
import logging

from django.db.models import Max
from django.db.transaction import atomic
from django.forms import model_to_dict
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from basics.models import GlobalCode
from mes.base_serializer import BaseModelSerializer
from recipe.models import Material, ProductInfo, ProductBatching, ProductBatchingDetail, \
    MaterialAttribute, ProductProcess, ProductProcessDetail, RecipeChangeHistory, RecipeChangeDetail
from production.models import PlanStatus, MaterialTankStatus
from mes.conf import COMMON_READ_ONLY_FIELDS

logger = logging.getLogger('api_log')


class MaterialSerializer(BaseModelSerializer):
    material_no = serializers.CharField(max_length=64, help_text='编码',
                                        validators=[UniqueValidator(queryset=Material.objects.filter(delete_flag=0),
                                                                    message='该原材料已存在')])
    material_type_name = serializers.CharField(source='material_type.global_name', read_only=True)
    package_unit_name = serializers.CharField(source='package_unit.global_name', read_only=True)
    update_user_name = serializers.CharField(source='last_updated_user.username', default=None, read_only=True)
    material_name = serializers.CharField(max_length=64, help_text='名称',
                                          validators=[UniqueValidator(queryset=Material.objects.filter(delete_flag=0),
                                                                      message='该原材料名称已存在')])

    def create(self, validated_data):
        validated_data['created_user'] = self.context['request'].user
        return super().create(validated_data)

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

    def create(self, validated_data):
        validated_data['created_user'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data['last_updated_user'] = self.context['request'].user
        return super().update(instance, validated_data)

    class Meta:
        model = ProductInfo
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductBatchingDetailSerializer(BaseModelSerializer):
    material = serializers.PrimaryKeyRelatedField(queryset=Material.objects.filter(delete_flag=False, use_flag=1))
    material_type = serializers.CharField(source='material.material_type.global_name', read_only=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True)
    provenance = serializers.SerializerMethodField(read_only=True)

    def get_provenance(self, obj):
        if obj.tank_no:
            tank = MaterialTankStatus.objects.filter(equip_no=obj.product_batching.equip.equip_no,
                                                     tank_no=obj.tank_no,
                                                     tank_type='1' if obj.type == 2 else '2',
                                                     material_no=obj.material.material_no).first()
            if tank:
                return tank.provenance
            else:
                return None
        else:
            return None

    class Meta:
        model = ProductBatchingDetail
        exclude = ('product_batching',)


class ProductBatchingListSerializer(BaseModelSerializer):
    product_name = serializers.CharField(source='product_info__product_name', read_only=True)
    created_username = serializers.CharField(source='created_user__username', read_only=True)
    stage_name = serializers.CharField(source="stage__global_name", read_only=True)
    site_name = serializers.CharField(source="site__global_name", read_only=True)
    dev_type_name = serializers.CharField(source='dev_type__category_name', default=None, read_only=True)
    equip_no = serializers.CharField(source='equip__equip_no', default=None, read_only=True)
    equip_name = serializers.CharField(source='equip__equip_name', default=None, read_only=True)
    sp_num = serializers.DecimalField(source='processes__sp_num', read_only=True, default=None, max_digits=3,
                                      decimal_places=1)
    dev_type = serializers.IntegerField(source='dev_type_id', read_only=True, default=None)
    category__category_name = serializers.CharField(source='equip__category__category_name',
                                                    default=None, read_only=True)
    submit_username = serializers.CharField(source='submit_user__username', read_only=True)
    reject_username = serializers.CharField(source='reject_user__username', read_only=True)
    used_username = serializers.CharField(source='used_user__username', read_only=True)
    obsolete_username = serializers.CharField(source='obsolete_user__username', read_only=True)
    last_update_username = serializers.CharField(source='last_updated_user__username', read_only=True)

    class Meta:
        model = ProductBatching
        fields = ('id', 'product_name', 'created_username', 'stage_name', 'site_name', 'dev_type_name',
                  'equip_no', 'equip_name', 'sp_num', 'stage_product_batch_no', 'production_time_interval',
                  'batching_type', 'created_date', 'batching_weight', 'used_type', 'dev_type',
                  'category__category_name', 'submit_username', 'reject_username', 'used_username', 'equip_id',
                  'obsolete_username', 'factory_id', 'site_id', 'product_info_id', 'precept', 'versions', 'stage_id',
                  'last_updated_date', 'is_synced', 'is_changed', 'last_update_username')


class ProductProcessDetailSerializer(BaseModelSerializer):
    condition_name = serializers.CharField(source='condition.condition', read_only=True, default=None)
    action_name = serializers.CharField(source='action.action', read_only=True, default=None)

    class Meta:
        model = ProductProcessDetail
        exclude = ('product_batching',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductProcessSerializer(BaseModelSerializer):
    class Meta:
        model = ProductProcess
        exclude = ('product_batching',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductBatchingCreateSerializer(BaseModelSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, required=False,
                                                       help_text="""
                                                           [{"sn": 序号, "material":原材料id, "auto_flag": true,
                                                           "actual_weight":重量, "standard_error":误差值}]""")
    processes = ProductProcessSerializer(help_text='步序data')
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
        stage_product_batch_no = validated_data.get('stage_product_batch_no')
        if stage_product_batch_no:
            # 传胶料编码则代表是特殊配方
            validated_data.pop('site', None)
            validated_data.pop('stage', None)
            validated_data.pop('versions', None)
            validated_data.pop('product_info', None)
        else:
            site = validated_data.get('site')
            stage = validated_data.get('stage')
            product_info = validated_data.get('product_info')
            versions = validated_data.get('versions')
            if not all([site, stage, product_info, versions]):
                raise serializers.ValidationError('参数不足')
            stage_product_batch_no = '{}-{}-{}-{}'.format(site.global_name, stage.global_name,
                                                          product_info.product_no, versions)
        stage_product_batch_no = stage_product_batch_no
        validated_data['stage_product_batch_no'] = stage_product_batch_no
        equip = validated_data['equip']
        if ProductBatching.objects.exclude(used_type=6).filter(
                stage_product_batch_no=stage_product_batch_no, equip=equip).exists():
            raise serializers.ValidationError('已存在相同机台的配方，请修改后重试！')
        batching_details = validated_data.pop('batching_details', None)
        processes = validated_data.pop('processes', None)
        process_details = validated_data.pop('process_details', None)
        validated_data['dev_type'] = validated_data['equip'].category
        validated_data['created_user'] = self.context["request"].user
        instance = super().create(validated_data)

        # 初始化配料相关重量
        batching_weight = manual_material_weight = auto_material_weight = 0

        # 增加配料详情
        if batching_details:
            batching_detail_list = [None] * len(batching_details)
            for i, detail in enumerate(batching_details):
                auto_flag = detail.get('auto_flag')
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

        # 增加步序和步序详情
        processes['product_batching'] = instance
        processes['created_user'] = self.context['request'].user
        ProductProcess.objects.create(**processes)
        batching_detail_list = []
        for detail in process_details:
            detail['product_batching'] = instance
            batching_detail_list.append(ProductProcessDetail(**detail))
        ProductProcessDetail.objects.bulk_create(batching_detail_list)

        # 新增原材料
        try:
            material_type = GlobalCode.objects.filter(global_type__type_name='原材料类别',
                                                      global_name=instance.stage.global_name).first()
            Material.objects.get_or_create(
                material_no=instance.stage_product_batch_no,
                material_name=instance.stage_product_batch_no,
                material_type=material_type,
                created_user=self.context['request'].user
            )
        except Exception as e:
            logger.error(e)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('factory', 'site', 'product_info', 'precept', 'stage_product_batch_no',
                  'stage', 'versions', 'batching_details', 'equip', 'id', 'dev_type',
                  'production_time_interval', 'processes', 'process_details')
        extra_kwargs = {
            'equip': {
                'required': True
            },
            'stage_product_batch_no': {
                'allow_blank': True,
                'allow_null': True,
                'required': False}
        }


class ProductBatchingRetrieveSerializer(BaseModelSerializer):
    batching_details = ProductBatchingDetailSerializer(many=True, required=False,
                                                       help_text="""
                                                       [{"sn": 序号, "material":原材料id, 
                                                       "actual_weight":重量, "error_range":误差值}]""")
    processes = ProductProcessSerializer(help_text='步序data', default=None)
    process_details = ProductProcessDetailSerializer(many=True, default=None)
    equip_no = serializers.CharField(source='equip.equip_no', default=None, read_only=True)
    equip_name = serializers.CharField(source='equip.equip_name', default=None, read_only=True)
    product_name = serializers.CharField(source='product_info.product_name', read_only=True)
    category__category_name = serializers.CharField(source='dev_type.category_name', default=None, read_only=True)

    class Meta:
        model = ProductBatching
        fields = ('id', 'equip_name', 'product_name', 'production_time_interval', 'factory',
                  'site', 'stage', 'batching_details', 'processes', 'process_details',
                  'equip_no', 'product_info', 'stage_product_batch_no', 'versions', 'category__category_name')


class ProductProcessCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductProcess
        exclude = ('product_batching',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductBatchingUpdateSerializer(ProductBatchingRetrieveSerializer):

    @atomic()
    def update(self, instance, validated_data):
        if instance.used_type not in (1, 4):
            raise serializers.ValidationError('操作无效！')
        batching_details = validated_data.pop('batching_details', None)
        processes = validated_data.pop('processes', None)
        process_details = validated_data.pop('process_details', None)
        validated_data['last_updated_user'] = self.context['request'].user
        instance = super().update(instance, validated_data)
        try:
            if instance.equip:
                change_data = {
                    'recipe_no': instance.stage_product_batch_no,
                    'equip_no': instance.equip.equip_no,
                    'dev_type': instance.equip.category.category_name,
                    'used_type': instance.used_type,
                    'created_time': instance.created_date,
                    'created_username': '' if not instance.created_user else instance.created_user.username,
                    'updated_time': datetime.now(),
                    'updated_username': self.context['request'].user.username
                }
                change_history, _ = RecipeChangeHistory.objects.update_or_create(
                    defaults=change_data,
                    **{'recipe_no': instance.stage_product_batch_no,
                       'equip_no': instance.equip.equip_no})
                # 当前配方详情
                current_batching_details = list(instance.batching_details.filter(
                    delete_flag=False).values('material__material_name', 'actual_weight', 'type', 'standard_error').order_by('type', 'id'))
                current_batching_details_dict = {i['material__material_name']: i for i in current_batching_details}
                # 修改后配方详情
                batching_details_dict = {i['material'].material_name: i for i in batching_details}
                added_material = set(batching_details_dict.keys()) - set(current_batching_details_dict.keys())
                deleted_material = set(current_batching_details_dict.keys()) - set(batching_details_dict.keys())
                common_material = set(current_batching_details_dict.keys()) & set(batching_details_dict.keys())
                desc = []
                change_detail_data = {1: [], 2: [], 3: [], 4: []}
                # {1: [{'type': 1, 'material_no': "aaa", 'flag': 'add', 'pv': '12', 'cv': '13'}], 2: "", 3: ""}
                # 比对配料
                if added_material:
                    desc.append('新增配料')
                    for i in added_material:
                        change_detail_data[1].append({'type': batching_details_dict[i]['type'],
                                                      'key': i,
                                                      'flag': '新增',
                                                      'cv': float(batching_details_dict[i]['actual_weight'])})
                if deleted_material:
                    desc.append('删除配料')
                    for i in deleted_material:
                        change_detail_data[1].append({'type': current_batching_details_dict[i]['type'],
                                                      'key': i,
                                                      'flag': '删除'})
                if common_material:
                    for i in common_material:
                        cv = batching_details_dict[i]['actual_weight']
                        pv = current_batching_details_dict[i]['actual_weight']

                        cv2 = batching_details_dict[i]['standard_error']
                        pv2 = current_batching_details_dict[i]['standard_error']
                        if pv != cv:
                            desc.append('配料修改')
                            change_detail_data[1].append({'type': batching_details_dict[i]['type'],
                                                          'key': i,
                                                          'flag': '修改',
                                                          'cv': float(cv),
                                                          'pv': float(pv)})
                        if pv2 != cv2:
                            desc.append('称量误差')
                            change_detail_data[4].append({'type': batching_details_dict[i]['type'],
                                                          'key': i,
                                                          'flag': '修改',
                                                          'cv': float(cv2),
                                                          'pv': float(pv2)})
                # 比对工艺参数
                if processes and hasattr(instance, 'processes'):
                    current_processes = model_to_dict(instance.processes)
                    for k, v in processes.items():
                        if not current_processes[k] == v:
                            desc.append('工艺修改')
                            if isinstance(v, bool):
                                cv = '启用' if v else '停用'
                                pv = '启用' if current_processes[k] else '停用'
                            else:
                                cv = float(v)
                                pv = float(current_processes[k])
                            change_detail_data[2].append({'type': None,
                                                          'key': ProductProcess._meta.get_field(k).help_text,
                                                          'flag': '修改',
                                                          'cv': cv,
                                                          'pv': pv})
                # 比对密炼步序
                if process_details and instance.process_details.exists():
                    p_pds = list(instance.process_details.filter(
                        delete_flag=False).order_by('id').values_list('action_id', flat=True))
                    v_pds = list(i['action'].id for i in process_details)
                    if not operator.eq(p_pds, v_pds):
                        desc.append('步序修改')
                        for i in process_details:
                            change_detail_data[3].append({'type': None,
                                                          'key': i['action'].action,
                                                          'flag': '修改',
                                                          'cv': None,
                                                          'pv': None})
                if desc:
                    RecipeChangeDetail.objects.create(
                        change_history=change_history,
                        desc='/'.join(set(desc)),
                        details=json.dumps(change_detail_data),
                        changed_username=self.context['request'].user.username
                    )
        except Exception:
            pass

        # 修改配料
        batching_weight = manual_material_weight = auto_material_weight = 0
        if batching_details is not None:
            instance.batching_details.filter().delete()
            batching_detail_list = [None] * len(batching_details)
            for i, detail in enumerate(batching_details):
                actual_weight = detail.get('actual_weight', 0)
                auto_flag = detail.get('auto_flag')
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
            # instance.save()
            instance = super().update(instance, validated_data)
        # 修改步序
        if processes:
            try:
                s = ProductProcessCreateSerializer(instance=instance.processes, data=processes)
                s.is_valid(raise_exception=True)
                s.save()
            except:
                processes['product_batching'] = instance
                ProductProcess.objects.create(**processes)
        if process_details is not None:
            process_detail_list = [None] * len(process_details)
            instance.process_details.filter().delete()
            for i, process_detail in enumerate(process_details):
                process_detail['product_batching'] = instance
                process_detail_list[i] = ProductProcessDetail(**process_detail)
            ProductProcessDetail.objects.bulk_create(process_detail_list)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('id', 'batching_details', 'production_time_interval', 'equip', 'processes', 'process_details', 'is_changed')


class ProductBatchingPartialUpdateSerializer(BaseModelSerializer):
    pass_flag = serializers.BooleanField(help_text='通过标志，1：通过, 0:驳回', write_only=True)

    def update(self, instance, validated_data):
        pass_flag = validated_data['pass_flag']
        if pass_flag:
            if instance.used_type == 1:  # 提交
                instance.submit_user = self.context['request'].user
                instance.submit_time = datetime.now()
                instance.used_type = 2
            elif instance.used_type == 2:  # 启用
                instance.used_type = 4
                instance.used_user = self.context['request'].user
                instance.used_time = datetime.now()
            elif instance.used_type == 5:
                instance.used_type = 1
        else:
            if instance.used_type in (4, 5):  # 弃用
                if instance.equip:
                    max_ids = PlanStatus.objects.filter(
                        product_no=instance.stage_product_batch_no,
                        equip_no=instance.equip.equip_no).values(
                        'plan_classes_uid').annotate(max_id=Max('id')).values_list('max_id', flat=True)
                    exist_status = set(PlanStatus.objects.filter(id__in=max_ids).values_list('status', flat=True))
                    if exist_status & {'已下达', '运行中'}:
                        raise serializers.ValidationError('该配方生产计划已下达或在运行中，无法废弃！')
                instance.obsolete_user = self.context['request'].user
                instance.used_type = 6
                instance.obsolete_time = datetime.now()
            else:  # 驳回
                instance.used_type = 5
                instance.reject_user = self.context['request'].user
                instance.reject_time = datetime.now()
        instance.last_updated_user = self.context['request'].user
        instance.save()
        RecipeChangeHistory.objects.filter(recipe_no=instance.stage_product_batch_no,
                                           equip_no=instance.equip.equip_no
                                           ).update(used_type=instance.used_type)
        return instance

    class Meta:
        model = ProductBatching
        fields = ('id', 'pass_flag')


class ProductBatchingDetailUploadSerializer(serializers.ModelSerializer):
    material__material_no = serializers.CharField(source='material.material_no')

    class Meta:
        model = ProductBatchingDetail
        fields = ('sn', 'material__material_no', 'actual_weight', 'standard_error', 'auto_flag', 'type')


class RecipeChangeHistorySerializer(serializers.ModelSerializer):
    change_desc = serializers.SerializerMethodField()

    def get_change_desc(self, obj):
        return list(obj.change_details.order_by('id').values('desc', 'changed_time__date', 'changed_username'))

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        change_desc = ret['change_desc']
        change_desc.insert(0, {'desc': '群控新增' if ret['origin'] == 1 else 'MES下传新增',
                               'changed_time__date': ret['created_time'][:10],
                               'changed_username': ret['created_username']})
        return ret

    class Meta:
        model = RecipeChangeHistory
        fields = '__all__'


class RecipeChangeDetailRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeChangeDetail
        fields = ('details', 'changed_time', 'changed_username')


class RecipeChangeHistoryRetrieveSerializer(RecipeChangeHistorySerializer):
    change_details = RecipeChangeDetailRetrieveSerializer(many=True)

    def to_representation(self, instance):
        ret = super(RecipeChangeHistoryRetrieveSerializer, self).to_representation(instance)
        change_details = ret['change_details']
        change_details.insert(0, {'details': '',
                                  'changed_time': ret['created_time'],
                                  'changed_username': ret['created_username']})
        return ret