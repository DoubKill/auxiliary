from django.db.transaction import atomic
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, ProductBatchingClassesPlan
from basics.models import PlanSchedule, WorkSchedulePlan, Equip, GlobalCode
from mes.conf import COMMON_READ_ONLY_FIELDS
from mes.base_serializer import BaseModelSerializer
from plan.uuidfield import UUidTools
from production.models import TrainsFeedbacks, PlanStatus
from recipe.models import ProductBatching
from work_station.api import IssueWorkStation
from work_station.models import IfdownShengchanjihua1


class ProductClassesPlanCreateSerializer(BaseModelSerializer):
    classes_name = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)
    classes = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.all(),
                                                 help_text='班次id（公共代码）', write_only=True)

    class Meta:
        model = ProductClassesPlan
        exclude = ('product_day_plan', 'work_schedule_plan', 'plan_classes_uid')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductDayPlanSerializer(BaseModelSerializer):
    """胶料日计划序列化"""
    pdp_product_classes_plan = ProductClassesPlanCreateSerializer(many=True,
                                                                  help_text="""
                                                                  {"sn":1,"plan_trains":1,"classes":班次id
                                                                  "time":"12.5","weight":1,"unit":1,"note":备注}
                                                                  """)
    equip_no = serializers.CharField(source='equip.equip_no', read_only=True, help_text='机台编号')
    category = serializers.CharField(source='equip.category', read_only=True, help_text='设备种类属性')
    product_no = serializers.CharField(source='product_batching.stage_product_batch_no', read_only=True,
                                       help_text='胶料编码')
    batching_weight = serializers.DecimalField(source='product_batching.batching_weight', decimal_places=2,
                                               max_digits=8,
                                               read_only=True, help_text='配料重量')
    production_time_interval = serializers.DecimalField(source='product_batching.production_time_interval',
                                                        read_only=True,
                                                        help_text='配料时间', decimal_places=2, max_digits=10)
    dev_type_name = serializers.CharField(source='product_batching.dev_type.global_name', read_only=True)

    class Meta:
        model = ProductDayPlan
        fields = ('id', 'equip', 'equip_no', 'category', 'plan_schedule',
                  'product_no', 'batching_weight', 'production_time_interval', 'product_batching',
                  'pdp_product_classes_plan', 'dev_type_name')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.filter(delete_flag=False),
                fields=('equip', 'product_batching', 'plan_schedule'),
                message="当天该机台已有相同的胶料计划数据，请修改后重试!"
            )
        ]

    @atomic()
    def create(self, validated_data):
        details = validated_data.pop('pdp_product_classes_plan', None)
        # 创建胶料日计划
        instance = super().create(validated_data)
        # 创建胶料日班次班次计划和原材料需求量
        for detail in details:
            if not detail['plan_trains']:
                continue
            classes = detail.pop('classes')
            work_schedule_plan = WorkSchedulePlan.objects.filter(classes=classes,
                                                                 plan_schedule=instance.plan_schedule).first()
            if not work_schedule_plan:
                raise serializers.ValidationError('暂无该班次排班数据')
            detail['plan_classes_uid'] = UUidTools.uuid1_hex(instance.equip.equip_no)
            detail['product_day_plan'] = instance
            detail['work_schedule_plan'] = work_schedule_plan
            pcp_obj = ProductClassesPlan.objects.create(**detail, created_user=self.context['request'].user)
            # 创建计划状态
            PlanStatus.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid, equip_no=instance.equip.equip_no,
                                      product_no=instance.product_batching.stage_product_batch_no,
                                      status='等待', operation_user=self.context['request'].user.username)
            for pbd_obj in instance.product_batching.batching_details.all():
                MaterialDemanded.objects.create(product_classes_plan=pcp_obj,
                                                work_schedule_plan=pcp_obj.work_schedule_plan,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                plan_classes_uid=pcp_obj.plan_classes_uid)
        return instance


class ProductBatchingClassesPlanSerializer(BaseModelSerializer):
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)

    class Meta:
        model = ProductBatchingClassesPlan
        exclude = ('product_batching_day_plan', 'classes_detail')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PalletFeedbacksPlanSerializer(BaseModelSerializer):
    equip_name = serializers.CharField(source='product_day_plan.equip.equip_no', read_only=True, help_text='机台名')
    stage_product_batch_no = serializers.CharField(source='product_day_plan.product_batching.stage_product_batch_no',
                                                   read_only=True, help_text='胶料编码')
    classes = serializers.CharField(source='work_schedule_plan.classes.global_name', read_only=True, help_text='班次')
    actual_trains = serializers.SerializerMethodField(read_only=True, help_text='实际车次')
    operation_user = serializers.SerializerMethodField(read_only=True, help_text='操作员')
    status = serializers.SerializerMethodField(read_only=True, help_text='状态')
    day_time = serializers.DateField(source='product_day_plan.plan_schedule.day_time', read_only=True)
    group = serializers.CharField(source='work_schedule_plan.group.global_name', read_only=True, help_text='班组')
    begin_time = serializers.DateTimeField(source='work_schedule_plan.start_time', read_only=True, help_text='开始时间')
    end_time = serializers.DateTimeField(source='work_schedule_plan.end_time', read_only=True, help_text='结束时间')

    def get_actual_trains(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).last()
        if tfb_obj:
            return tfb_obj.actual_trains
        else:
            return None

    def get_operation_user(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).last()
        if tfb_obj:
            return tfb_obj.operation_user
        else:
            return None

    def get_status(self, obj):
        plan_status = PlanStatus.objects.filter(plan_classes_uid=obj.plan_classes_uid).last()
        if plan_status:
            return plan_status.status
        else:
            return None

    class Meta:
        model = ProductClassesPlan
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class UpRegulationSerializer(BaseModelSerializer):
    """上调"""
    equip_name = serializers.CharField(write_only=True, help_text='机台名', required=False)
    classes = serializers.CharField(write_only=True, help_text='班次', required=False)
    product_batching = serializers.CharField(write_only=True, help_text='配方', required=False)
    begin_times = serializers.DateTimeField(write_only=True, help_text='开始时间', required=False)
    end_times = serializers.DateTimeField(write_only=True, help_text='结束时间', required=False)

    class Meta:
        model = ProductClassesPlan
        fields = ('equip_name', 'classes', 'product_batching', 'begin_times', 'end_times')
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).last()
        # for p_obj in p_status:
        if p_status.status != '等待':
            raise serializers.ValidationError({'equip_name': '只有等待中的计划才能上调'})
        update_dict = {'delete_flag': False}
        equip_name = validated_data.get('equip_name', None)
        if equip_name:
            update_dict['product_day_plan__equip__equip_name'] = equip_name
        classes = validated_data.get('classes', None)
        if classes:
            update_dict['work_schedule_plan__classes__global_name'] = classes
        product_batching = validated_data.get('product_batching', None)
        if product_batching:
            update_dict['product_day_plan__product_batching__stage_product_batch_no'] = product_batching
        begin_times = validated_data.get('begin_times', None)
        end_times = validated_data.get('end_times', None)
        if begin_times and end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times,
                                                             end_time__lte=end_times)
        elif begin_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times)
        elif end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, end_time__lte=end_times)
        else:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict)
        last_obj = pcp_queryset.filter(sn__lt=instance.sn).last()
        if last_obj:
            snsn = last_obj.sn
            last_obj.sn = instance.sn
            last_obj.save()

            instance.sn = snsn
            instance.save()
            return instance
        raise serializers.ValidationError({'equip_name': '当前计划无法上调'})


class DownRegulationSerializer(BaseModelSerializer):
    """下调"""
    equip_name = serializers.CharField(write_only=True, help_text='机台名', required=False)
    classes = serializers.CharField(write_only=True, help_text='班次', required=False)
    product_batching = serializers.CharField(write_only=True, help_text='配方', required=False)
    begin_times = serializers.DateTimeField(write_only=True, help_text='开始时间', required=False)
    end_times = serializers.DateTimeField(write_only=True, help_text='结束时间', required=False)

    class Meta:
        model = ProductClassesPlan
        fields = ('equip_name', 'classes', 'product_batching', 'begin_times', 'end_times')
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).last()
        # for p_obj in p_status:
        if p_status.status != '等待':
            raise serializers.ValidationError({'equip_name': '只有等待中的计划才能下调'})
        update_dict = {'delete_flag': False}
        equip_name = validated_data.get('equip_name', None)
        if equip_name:
            update_dict['product_day_plan__equip__equip_name'] = equip_name
        classes = validated_data.get('classes', None)
        if classes:
            update_dict['classes_detail__classes__global_name'] = classes
        product_batching = validated_data.get('product_batching', None)
        if product_batching:
            update_dict['product_day_plan__product_batching__stage_product_batch_no'] = product_batching
        begin_times = validated_data.get('begin_times', None)
        end_times = validated_data.get('end_times', None)
        if begin_times and end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times,
                                                             end_time__lte=end_times)
        elif begin_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times)
        elif end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, end_time__lte=end_times)
        else:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict)
        last_obj = pcp_queryset.filter(sn__gt=instance.sn).first()
        if last_obj:
            snsn = last_obj.sn
            last_obj.sn = instance.sn
            last_obj.save()

            instance.sn = snsn
            instance.save()
            return instance
        raise serializers.ValidationError({'equip_name': '当前计划无法下调'})


class UpdateTrainsSerializer(BaseModelSerializer):
    '''修改车次和重传'''
    trains = serializers.IntegerField(write_only=True, help_text='修改车次')

    class Meta:
        model = ProductClassesPlan
        fields = ('trains',)
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).all()
        if not p_status:
            raise serializers.ValidationError({'trains': "计划状态变更没有数据"})
        for p_obj in p_status:
            if p_obj.status != '运行中':
                raise serializers.ValidationError({'trains': '只有运行中的计划才可以修改车次'})
        trains = validated_data.get('trains')
        instance.plan_trains = trains
        instance.save()

        # plan_id = instance.id
        # equip_name = instance.product_day_plan.equip.equip_name
        # ps_obj = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).last()
        # if not ps_obj:
        #     raise serializers.ValidationError({'trains': "计划状态变更没有数据"})
        # 计划状态变更表的状态也需要改变
        # ps_obj.status = '运行中'
        # ps_obj.save()
        ifcjh_obj = IfdownShengchanjihua1.objects.filter(id=instance.id).first()
        if ifcjh_obj.recstatus == "运行中":
            temp_data = {
                'id': instance.id,  # id
                'setno': instance.plan_trains,  # 设定车次
                'remark': 'u',
                'recstatus': '车次需更新'
            }
        elif ifcjh_obj.recstatus == "配方需重传":
            temp_data = {
                'id': instance.id,  # id
                'setno': instance.plan_trains,  # 设定车次
                'remark': 'u',
                'recstatus': '配方车次需更新'
            }
        temp = IssueWorkStation('IfdownShengchanjihua1', temp_data)
        temp.update_to_db()
        return instance


class ProductClassesPlanSerializer(BaseModelSerializer):
    # class Meta:
    #     model = ProductClassesPlan
    #     fields = '__all__'

    work_schedule_plan = serializers.CharField()

    class Meta:
        model = ProductClassesPlan
        fields = (
            'sn', 'plan_trains', 'time', 'weight', 'unit', 'work_schedule_plan', 'plan_classes_uid',
            'note')


class PlanReceiveSerializer(BaseModelSerializer):
    equip = serializers.CharField()
    product_batching = serializers.CharField()
    plan_schedule = serializers.CharField()
    pdp_product_classes_plan = ProductClassesPlanSerializer(many=True)

    def validate(self, attrs):
        plan_schedule = attrs['plan_schedule']
        product_batching = attrs.get('product_batching')
        equip = attrs.get('equip')
        if ProductDayPlan.objects.filter(plan_schedule__plan_schedule_no=plan_schedule):
            raise serializers.ValidationError('该计划已存在， 请重试！')
        try:
            equip = Equip.objects.get(equip_no=equip)
            product_batching = ProductBatching.objects.get(stage_product_batch_no=product_batching)
            plan_schedule = PlanSchedule.objects.get(plan_schedule_no=plan_schedule)
        except Equip.DoesNotExist:
            raise serializers.ValidationError('上辅机机台{}不存在'.format(attrs.get('equip')))
        except ProductBatching.DoesNotExist:
            raise serializers.ValidationError('胶料配料标准{}不存在'.format(attrs.get('product_batching')))
        except PlanSchedule.DoesNotExist:
            raise serializers.ValidationError('排班管理{}不存在'.format(attrs.get('plan_schedule')))
        except Exception as e:
            raise serializers.ValidationError('相关表没有数据')
        attrs['product_batching'] = product_batching
        attrs['plan_schedule'] = plan_schedule
        attrs['equip'] = equip
        return attrs

    @atomic()
    def create(self, validated_data):
        pdp_product_classes_plan = validated_data.pop('pdp_product_classes_plan')
        instance = super().create(validated_data)
        product_classes_list = [None] * len(pdp_product_classes_plan)
        for i, detail in enumerate(pdp_product_classes_plan):
            detail['product_day_plan'] = instance
            work_schedule_plan_no = detail['work_schedule_plan']
            detail['work_schedule_plan'] = WorkSchedulePlan.objects.get(work_schedule_plan_no=work_schedule_plan_no)
            product_classes_list[i] = ProductClassesPlan(**detail)
        pcp_obj_list = ProductClassesPlan.objects.bulk_create(product_classes_list)
        print(pcp_obj_list)
        for pcp_obj in pcp_obj_list:
            PlanStatus.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid, equip_no=instance.equip.equip_no,
                                      product_no=instance.product_batching.stage_product_batch_no,
                                      status='等待', operation_user=self.context['request'].user.username)

        return instance

    class Meta:
        model = ProductDayPlan
        fields = ('equip', 'product_batching', 'plan_schedule', 'pdp_product_classes_plan',)
        read_only_fields = COMMON_READ_ONLY_FIELDS
