import copy
import datetime

from django.db.models import Max
from django.db.transaction import atomic
from rest_framework import serializers
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, ProductBatchingDayPlan, \
    ProductBatchingClassesPlan, MaterialRequisitionClasses
from basics.models import PlanSchedule, WorkSchedule, ClassesDetail, WorkSchedulePlan
from mes.conf import COMMON_READ_ONLY_FIELDS
from mes.base_serializer import BaseModelSerializer
from plan.uuidfield import UUidTools
from production.models import PalletFeedbacks, TrainsFeedbacks, PlanStatus
from recipe.models import ProductBatchingDetail, ProductBatching


class ProductClassesPlanSerializer(BaseModelSerializer):
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)

    class Meta:
        model = ProductClassesPlan
        exclude = ('product_day_plan', 'classes_detail')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductDayPlanSerializer(BaseModelSerializer):
    """胶料日计划序列化"""
    pdp_product_classes_plan = ProductClassesPlanSerializer(many=True,
                                                            help_text='{"sn":1,"plan_trains":1,"time":"12:12:12","weight":1,"unit":1}')
    plan_date = serializers.DateField(help_text="2020-07-31", write_only=True)
    equip_no = serializers.CharField(source='equip.equip_no', read_only=True, help_text='机台编号')
    category = serializers.CharField(source='equip.category', read_only=True, help_text='设备种类属性')
    product_no = serializers.CharField(source='product_batching.stage_product_batch_no', read_only=True,
                                       help_text='胶料编码')
    batching_weight = serializers.DecimalField(source='product_batching.batching_weight', decimal_places=2,
                                               max_digits=8,
                                               read_only=True, help_text='配料重量')
    batching_time_interval = serializers.TimeField(source='product_batching.batching_time_interval', read_only=True,
                                                   help_text='配料时间')

    class Meta:

        model = ProductDayPlan
        fields = ('id',
                  'plan_date', 'equip', 'equip_no', 'category', 'product_no', 'batching_weight',
                  'batching_time_interval',
                  'product_batching',
                  'pdp_product_classes_plan')
        read_only_fields = COMMON_READ_ONLY_FIELDS

    def validate_product_batching(self, value):
        pb_obj = value
        for pbd_obj in pb_obj.batching_details.all():
            if not pbd_obj.actual_weight:
                raise serializers.ValidationError('当前胶料配料标准详情数据不存在')
        return value

    def validate_plan_date(self, value):
        if not PlanSchedule.objects.filter(day_time=value):
            raise serializers.ValidationError('当前计划时间不存在')
        return value

    def validate_pdp_product_classes_plan(self, value):
        if len(value) != 3:
            raise serializers.ValidationError('无效数据，必须有三条')
        return value

    @atomic()
    def create(self, validated_data):
        pdp_dic = {}
        pdp_dic['equip'] = validated_data.pop('equip')
        pdp_dic['product_batching'] = validated_data.pop('product_batching')
        plan_date = validated_data.pop('plan_date')
        pdp_dic['plan_schedule'] = PlanSchedule.objects.filter(day_time=plan_date).first()
        pdp_dic['created_user'] = self.context['request'].user
        instance = super().create(pdp_dic)
        details = validated_data['pdp_product_classes_plan']
        # WorkSchedule.objects.filter(plan_schedule__day_time=plan_date).first()
        cd_queryset = ClassesDetail.objects.filter(
            work_schedule=WorkSchedule.objects.filter(plan_schedule__day_time=plan_date).first())
        # 创建班次计划和原材料需求量
        i = 0
        for detail in details:
            detail_dic = dict(detail)
            detail_dic['plan_classes_uid'] = UUidTools.uuid1_hex()
            detail_dic['product_day_plan'] = instance
            detail_dic['classes_detail'] = cd_queryset[i]
            # cd_queryset[i].cd_product_classes_plan.end_time
            if cd_queryset[i].cd_product_classes_plan.all():
                detail_dic['begin_time'] = cd_queryset[i].cd_product_classes_plan.all().aggregate(Max("end_time"))[
                    'end_time__max']
            else:
                detail_dic['begin_time'] = cd_queryset[i].start_time
            detail_dic['end_time'] = detail_dic['begin_time'] + datetime.timedelta(
                seconds=detail_dic['time'].hour * 3600 + detail_dic['time'].minute * 60 + detail_dic['time'].second)
            i += 1
            pcp_obj = ProductClassesPlan.objects.create(**detail_dic, created_user=self.context['request'].user)
            for pbd_obj in instance.product_batching.batching_details.all():
                MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                plan_classes_uid=pcp_obj.plan_classes_uid,
                                                plan_schedule=instance.plan_schedule)
        return instance

    @atomic()
    def update(self, instance, validated_data):
        update_pcp_list = validated_data.pop('pdp_product_classes_plan', None)
        day_time = validated_data.pop('plan_date', None)
        if day_time:
            validated_data['plan_schedule'] = PlanSchedule.objects.filter(day_time=day_time).first()
        else:
            validated_data['plan_schedule'] = instance.plan_schedule
        validated_data['last_updated_user'] = self.context['request'].user
        pdp_obj = super().update(instance, validated_data)
        # 若没有修改班级计划
        if update_pcp_list is None or len(update_pcp_list) == 0:
            c_queryset = pdp_obj.pdp_product_classes_plan.all()
            for c_obj in c_queryset:
                MaterialDemanded.objects.filter(plan_classes_uid=c_obj.plan_classes_uid).delete()
            for pcp_obj in pdp_obj.pdp_product_classes_plan.all():
                for pbd_obj in pdp_obj.product_batching.batching_details.all():
                    MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                    material=pbd_obj.material,
                                                    material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                    plan_classes_uid=pcp_obj.plan_classes_uid,
                                                    plan_schedule=pdp_obj.plan_schedule)
            return pdp_obj
        # 删除原材料需求量和班次计划，再重写
        c_queryset = pdp_obj.pdp_product_classes_plan.all()
        for c_obj in c_queryset:
            MaterialDemanded.objects.filter(plan_classes_uid=c_obj.plan_classes_uid).delete()
        be_list = []
        for be_obj in c_queryset:
            be_dict = {}
            be_dict['begin_time'] = be_obj.begin_time
            be_dict['end_time'] = be_obj.end_time
            be_list.append(be_dict)
        c_queryset.delete()
        cd_queryset = ClassesDetail.objects.filter(
            work_schedule=WorkSchedule.objects.filter(plan_schedule__day_time=day_time).first())
        i = 0
        for update_pcp in update_pcp_list:
            update_pcp = dict(update_pcp)
            update_pcp['product_day_plan'] = instance
            update_pcp['classes_detail'] = cd_queryset[i]
            update_pcp['begin_time'] = be_list[i]['begin_time']
            update_pcp['end_time'] = be_list[i]['end_time']
            update_pcp['plan_classes_uid'] = UUidTools.uuid1_hex()
            update_pcp['last_updated_user'] = self.context['request'].user
            pcp_obj = ProductClassesPlan.objects.create(**update_pcp, created_user=self.context['request'].user)
            i += 1
            for pbd_obj in pdp_obj.product_batching.batching_details.all():
                MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                plan_classes_uid=pcp_obj.plan_classes_uid,
                                                plan_schedule=pdp_obj.plan_schedule)
        return pdp_obj


class ProductBatchingClassesPlanSerializer(BaseModelSerializer):
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)

    class Meta:
        model = ProductBatchingClassesPlan
        exclude = ('product_batching_day_plan', 'classes_detail')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductBatchingDayPlanSerializer(BaseModelSerializer):
    """配料小料日计划序列化"""

    pdp_product_batching_classes_plan = ProductBatchingClassesPlanSerializer(many=True,
                                                                             help_text='{"sn":1,"bags_qty":1,"unit":"1"}')
    plan_date = serializers.DateField(help_text="2020-07-31", write_only=True)
    plan_date_time = serializers.DateField(source='plan_schedule.day_time', read_only=True)
    equip_no = serializers.CharField(source='equip.equip_no', read_only=True, help_text='设备编号')
    catagory_name = serializers.CharField(source='equip.category.equip_type', read_only=True, help_text='设备种类属性')
    product_no = serializers.CharField(source='product_batching.stage_product_batch_no', read_only=True,
                                       help_text='胶料编码')
    manual_material_weight = serializers.DecimalField(source='product_batching.manual_material_weight',
                                                      decimal_places=2,
                                                      max_digits=8,
                                                      read_only=True, help_text='配料小料重量')

    class Meta:
        model = ProductBatchingDayPlan
        fields = ('id', 'equip_no', 'plan_date_time', 'catagory_name', 'product_no', 'manual_material_weight',
                  'equip', 'product_batching', 'plan_date', 'bags_total_qty', 'product_day_plan',
                  'pdp_product_batching_classes_plan', 'product_day_plan')
        read_only_fields = COMMON_READ_ONLY_FIELDS
        extra_kwargs = {
            'product_day_plan': {
                'required': False
            }
        }

    def validate_product_batching(self, value):
        pb_obj = value
        for pbd_obj in pb_obj.batching_details.all():
            if not pbd_obj.actual_weight:
                raise serializers.ValidationError('当前胶料配料标准详情数据不存在')
        return value

    def validate_plan_date(self, value):
        if not PlanSchedule.objects.filter(day_time=value).first():
            raise serializers.ValidationError('当前计划时间不存在')
        return value

    def validate_pdp_product_batching_classes_plan(self, value):
        if len(value) != 3:
            raise serializers.ValidationError('无效数据，必须有三条')
        return value

    @atomic()
    def create(self, validated_data):

        pdp_dic = {}
        pdp_dic['equip'] = validated_data.pop('equip')
        pdp_dic['product_batching'] = validated_data.pop('product_batching')
        plan_date = validated_data.pop('plan_date')
        pdp_dic['plan_schedule'] = PlanSchedule.objects.filter(day_time=plan_date).first()
        pdp_dic['bags_total_qty'] = validated_data.pop('bags_total_qty')
        pdp_dic['product_day_plan'] = validated_data.pop('product_day_plan', None)
        if pdp_dic['product_day_plan'] == None:
            pdp_dic.pop('product_day_plan')
        pdp_dic['created_user'] = self.context['request'].user

        instance = super().create(pdp_dic)
        details = validated_data['pdp_product_batching_classes_plan']
        cd_queryset = ClassesDetail.objects.filter(
            work_schedule=WorkSchedule.objects.filter(plan_schedule__day_time=plan_date).first())
        i = 0
        for detail in details:
            detail_dic = dict(detail)
            detail_dic['plan_classes_uid'] = UUidTools.uuid1_hex()
            detail_dic['product_batching_day_plan'] = instance
            detail_dic['classes_detail'] = cd_queryset[i]
            i += 1
            pcp_obj = ProductBatchingClassesPlan.objects.create(**detail_dic, created_user=self.context['request'].user)
            for pbd_obj in instance.product_batching.batching_details.all():
                MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.bags_qty,
                                                plan_classes_uid=pcp_obj.plan_classes_uid,
                                                plan_schedule=instance.plan_schedule)
        return instance

    @atomic()
    def update(self, instance, validated_data):
        update_pcp_list = validated_data.pop('pdp_product_batching_classes_plan', None)
        day_time = validated_data.pop('plan_date', None)
        if day_time:
            validated_data['plan_schedule'] = PlanSchedule.objects.filter(day_time=day_time).first()
        else:
            validated_data['plan_schedule'] = instance.plan_schedule
        validated_data['last_updated_user'] = self.context['request'].user
        pdp_obj = super().update(instance, validated_data)
        if update_pcp_list is None:
            c_queryset = pdp_obj.pdp_product_batching_classes_plan.all()
            for c_obj in c_queryset:
                MaterialDemanded.objects.filter(plan_classes_uid=c_obj.plan_classes_uid).delete()
            for pcp_obj in pdp_obj.pdp_product_batching_classes_plan.all():
                for pbd_obj in pdp_obj.product_batching.batching_details.all():
                    MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                    material=pbd_obj.material,
                                                    material_demanded=pbd_obj.actual_weight * pcp_obj.bags_qty,
                                                    plan_classes_uid=pcp_obj.plan_classes_uid,
                                                    plan_schedule=pdp_obj.plan_schedule)
            return pdp_obj
        # 删除原材料需求量和班次计划，再重写
        c_queryset = pdp_obj.pdp_product_batching_classes_plan.all()
        for c_obj in c_queryset:
            MaterialDemanded.objects.filter(plan_classes_uid=c_obj.plan_classes_uid).delete()
        c_queryset.delete()
        cd_queryset = ClassesDetail.objects.filter(
            work_schedule=WorkSchedule.objects.filter(plan_schedule__day_time=day_time).first())
        i = 0
        for update_pcp in update_pcp_list:
            update_pcp = dict(update_pcp)
            update_pcp['product_batching_day_plan'] = instance
            update_pcp['classes_detail'] = cd_queryset[i]
            update_pcp['plan_classes_uid'] = UUidTools.uuid1_hex()
            update_pcp['last_updated_user'] = self.context['request'].user
            # ProductBatchingClassesPlan.objects.create(**update_pcp)
            pcp_obj = ProductBatchingClassesPlan.objects.create(**update_pcp, created_user=self.context['request'].user)
            i += 1
            for pbd_obj in pdp_obj.product_batching.batching_details.all():
                MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.bags_qty,
                                                plan_classes_uid=pcp_obj.plan_classes_uid,
                                                plan_schedule=pdp_obj.plan_schedule)
        return pdp_obj


class MaterialRequisitionSerializer(BaseModelSerializer):
    class Meta:
        model = MaterialRequisitionClasses
        fields = '__all__'


class MaterialDemandedSerializer(BaseModelSerializer):
    """原材料需求量序列化"""
    md_material_requisition_classes = MaterialRequisitionSerializer(read_only=True, many=True)
    material_name = serializers.CharField(source='material.material_name', read_only=True, help_text='原材料名称')
    classes_name = serializers.CharField(source='classes.classes_name', read_only=True)
    material_type = serializers.CharField(source='material.material_type', read_only=True)
    material_no = serializers.CharField(source='material.material_no', read_only=True)

    # material_name = serializers.CharField(source='material.material_name', read_only=True)

    class Meta:
        model = MaterialDemanded
        fields = ('id', 'material_name', 'classes_name', 'material_type', 'material_no',
                  'classes', 'material', 'plan_schedule', 'material_demanded', 'md_material_requisition_classes')


class MaterialRequisitionClassesSerializer(BaseModelSerializer):
    material_ids = serializers.ListField(help_text='三个需求量id', write_only=True)
    plan_date = serializers.DateField(help_text='日期', write_only=True)
    weights = serializers.ListField(help_text='早中晚领料计划的重量', write_only=True)

    class Meta:
        model = MaterialRequisitionClasses
        fields = ('material_ids', 'plan_date', 'weights',)
        read_only_fields = COMMON_READ_ONLY_FIELDS

    # def validate_material_id(self, value):
    #     if not MaterialDemanded.objects.filter(id=value, delete_flag=False):
    #         raise serializers.ValidationError('当前原材料需要量不存在')
    #     return value

    def validate_plan_date(self, value):
        if not PlanSchedule.objects.filter(day_time=value).first():
            raise serializers.ValidationError('当前计划时间不存在')
        return value

    def validate_weights(self, value):
        if len(value) != 3:
            raise serializers.ValidationError('无效数据，必须有三条')
        return value

    @atomic()
    def create(self, validated_data):
        plan_date = validated_data.pop('plan_date')
        weights = validated_data.pop('weights')
        material_ids = validated_data.pop('material_ids')
        for material_id in material_ids:
            mrc_queryset = MaterialDemanded.objects.filter(id=material_id).first().md_material_requisition_classes.all()
            if mrc_queryset:
                mrc_queryset.delete()
        cd_queryset = ClassesDetail.objects.filter(
            work_schedule=WorkSchedule.objects.filter(plan_schedule__day_time=plan_date).first())
        i = 0
        for weight in weights:
            mrc_dic = {}
            mrc_dic['plan_classes_uid'] = UUidTools.uuid1_hex()
            mrc_dic['created_user'] = self.context['request'].user
            mrc_dic['weight'] = weight
            mrc_dic['classes_detail'] = cd_queryset[i]
            mrc_dic['unit'] = 'kg'
            instance = MaterialRequisitionClasses.objects.create(**mrc_dic)
            for material_id in material_ids:
                instance.material_demanded.add(MaterialDemanded.objects.filter(id=material_id).first())
            i += 1
        return instance


class ProductDayPlanCopySerializer(BaseModelSerializer):
    src_date = serializers.DateField(help_text="2020-07-31", write_only=True)
    dst_date = serializers.DateField(help_text="2020-08-01", write_only=True)

    class Meta:
        model = ProductDayPlan
        fields = ('src_date', 'dst_date')

    def validate_src_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value).first()
        if not instance:
            raise serializers.ValidationError('被复制的日期没有计划时间')
        pdp_obj = ProductDayPlan.objects.filter(plan_schedule=instance)
        if not pdp_obj:
            raise serializers.ValidationError('被复制的日期没有计划')
        return value

    def validate_dst_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value)
        if not instance:
            raise serializers.ValidationError('新建的日期没有计划时间')
        return value

    def validate(self, attrs):
        src_date = attrs['src_date']
        dst_date = attrs['dst_date']
        if dst_date < src_date:
            raise serializers.ValidationError('新建日期不能小于被复制日期')
        return attrs

    @atomic()
    def create(self, validated_data):
        src_date = validated_data.pop('src_date')
        dst_date = validated_data.pop('dst_date')
        ps_obj = PlanSchedule.objects.filter(day_time=dst_date).first()
        pdp_queryset = ProductDayPlan.objects.filter(plan_schedule__day_time=src_date, delete_flag=False)
        delete_pdp_queryset = ProductDayPlan.objects.filter(plan_schedule__day_time=dst_date, delete_flag=False)
        if delete_pdp_queryset:
            ProductDayPlan.objects.filter(plan_schedule__day_time=dst_date, delete_flag=False).update(delete_flag=True,
                                                                                                      delete_user=
                                                                                                      self.context[
                                                                                                          'request'].user)
            for delete_pdp_obj in delete_pdp_queryset:
                delete_pcp_queryset = ProductClassesPlan.objects.filter(product_day_plan=delete_pdp_obj,
                                                                        delete_flag=False)
                if delete_pcp_queryset:
                    for delete_pcp_obj in delete_pcp_queryset:
                        if MaterialDemanded.objects.filter(plan_classes_uid=delete_pcp_obj.plan_classes_uid,
                                                           delete_flag=False):
                            MaterialDemanded.objects.filter(plan_classes_uid=delete_pcp_obj.plan_classes_uid,
                                                            delete_flag=False).update(
                                delete_flag=True,
                                delete_user=self.context[
                                    'request'].user)
                    ProductClassesPlan.objects.filter(product_day_plan=delete_pdp_obj,
                                                      delete_flag=False).update(delete_flag=True,
                                                                                delete_user=self.context[
                                                                                    'request'].user)
        for pdp_obj in pdp_queryset:
            instance = ProductDayPlan.objects.create(equip=pdp_obj.equip, product_batching=pdp_obj.product_batching,
                                                     plan_schedule=ps_obj, created_user=self.context['request'].user)

            pc_queryset = ProductClassesPlan.objects.filter(product_day_plan=pdp_obj)
            for pc_obj in pc_queryset:
                pcp_obj = ProductClassesPlan.objects.create(product_day_plan=instance, sn=pc_obj.sn,
                                                            plan_trains=pc_obj.plan_trains,
                                                            time=pc_obj.time,
                                                            weight=pc_obj.weight, unit=pc_obj.unit,
                                                            classes_detail=pc_obj.classes_detail,
                                                            plan_classes_uid=UUidTools.uuid1_hex(),
                                                            created_user=self.context['request'].user)
                for pbd_obj in instance.product_batching.batching_details.all():
                    MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                    material=pbd_obj.material,
                                                    material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                    plan_classes_uid=pcp_obj.plan_classes_uid,
                                                    plan_schedule=instance.plan_schedule)
        return instance


class ProductBatchingDayPlanCopySerializer(BaseModelSerializer):
    src_date = serializers.DateField(help_text="2020-07-31", write_only=True)
    dst_date = serializers.DateField(help_text="2020-08-01", write_only=True)

    class Meta:
        model = ProductBatchingDayPlan
        fields = ('src_date', 'dst_date')

    def validate_src_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value).first()
        if not instance:
            raise serializers.ValidationError('被复制的日期没有计划时间')
        pdp_obj = ProductBatchingDayPlan.objects.filter(plan_schedule=instance)
        if not pdp_obj:
            raise serializers.ValidationError('被复制的日期没有计划')
        return value

    def validate_dst_date(self, value):
        instance = PlanSchedule.objects.filter(day_time=value)
        if not instance:
            raise serializers.ValidationError('新建的日期没有计划时间')
        return value

    def validate(self, attrs):
        src_date = attrs['src_date']
        dst_date = attrs['dst_date']
        if dst_date < src_date:
            raise serializers.ValidationError('新建日期不能小于被复制日期')
        return attrs

    @atomic()
    def create(self, validated_data):

        src_date = validated_data.pop('src_date')
        dst_date = validated_data.pop('dst_date')
        ps_obj = PlanSchedule.objects.filter(day_time=dst_date).first()
        pbdp_queryset = ProductBatchingDayPlan.objects.filter(plan_schedule__day_time=src_date, delete_flag=False)
        delete_pdp_queryset = ProductBatchingDayPlan.objects.filter(plan_schedule__day_time=dst_date, delete_flag=False)
        if delete_pdp_queryset:
            ProductBatchingDayPlan.objects.filter(plan_schedule__day_time=dst_date, delete_flag=False).update(
                delete_flag=True,
                delete_user=
                self.context[
                    'request'].user)
            for delete_pdp_obj in delete_pdp_queryset:
                delete_pbcp_queryset = ProductBatchingClassesPlan.objects.filter(
                    product_batching_day_plan=delete_pdp_obj, delete_flag=False)
                if delete_pbcp_queryset:
                    for delete_pbcp_obj in delete_pbcp_queryset:
                        if MaterialDemanded.objects.filter(plan_classes_uid=delete_pbcp_obj.plan_classes_uid,
                                                           delete_flag=False):
                            MaterialDemanded.objects.filter(plan_classes_uid=delete_pbcp_obj.plan_classes_uid,
                                                            delete_flag=False).update(
                                delete_flag=True,
                                delete_user=
                                self.context[
                                    'request'].user)
                    ProductBatchingClassesPlan.objects.filter(
                        product_batching_day_plan=delete_pdp_obj, delete_flag=False).update(
                        delete_flag=True,
                        delete_user=self.context[
                            'request'].user)
        for pbdp_obj in pbdp_queryset:
            instance = ProductBatchingDayPlan.objects.create(equip=pbdp_obj.equip,
                                                             product_batching=pbdp_obj.product_batching,
                                                             plan_schedule=ps_obj,
                                                             bags_total_qty=pbdp_obj.bags_total_qty,
                                                             product_day_plan=pbdp_obj.product_day_plan,
                                                             created_user=self.context['request'].user)
            pc_queryset = ProductBatchingClassesPlan.objects.filter(product_batching_day_plan=pbdp_obj)
            for pc_obj in pc_queryset:
                pcp_obj = ProductBatchingClassesPlan.objects.create(product_batching_day_plan=instance,
                                                                    sn=pc_obj.sn, bags_qty=pc_obj.bags_qty,
                                                                    # time=pc_obj.time,
                                                                    # weight=pc_obj.weight, unit=pc_obj.unit,
                                                                    classes_detail=pc_obj.classes_detail,
                                                                    plan_classes_uid=UUidTools.uuid1_hex(),
                                                                    created_user=self.context['request'].user)
                for pbd_obj in instance.product_batching.batching_details.all():
                    MaterialDemanded.objects.create(classes=pcp_obj.classes_detail,
                                                    material=pbd_obj.material,
                                                    material_demanded=pbd_obj.actual_weight * pcp_obj.bags_qty,
                                                    plan_classes_uid=pcp_obj.plan_classes_uid,
                                                    plan_schedule=instance.plan_schedule
                                                    )
        return instance


class PalletFeedbacksPlanSerializer(BaseModelSerializer):
    equip_name = serializers.CharField(source='product_day_plan.equip.equip_name', read_only=True, help_text='机台名')
    stage_product_batch_no = serializers.CharField(source='product_day_plan.product_batching.stage_product_batch_no',
                                                   read_only=True, help_text='胶料编码')
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True, help_text='班次')
    actual_trains = serializers.SerializerMethodField(read_only=True, help_text='实际车次')
    operation_user = serializers.SerializerMethodField(read_only=True, help_text='操作员')
    status = serializers.SerializerMethodField(read_only=True, help_text='状态')
    day_time = serializers.DateField(source='product_day_plan.plan_schedule.day_time', read_only=True)
    group = serializers.CharField(source='work_schedule_plan.group.global_name', read_only=True, help_text='班组')
    begin_time = serializers.DateTimeField(source='work_schedule_plan.start_time', read_only=True, help_text='开始时间')
    end_time = serializers.DateTimeField(source='work_schedule_plan.end_time', read_only=True, help_text='结束时间')

    def get_actual_trains(self, object):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=object.plan_classes_uid).last()
        if tfb_obj:
            return tfb_obj.actual_trains
        else:
            return None

    def get_operation_user(self, object):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=object.plan_classes_uid).last()
        if tfb_obj:
            return tfb_obj.operation_user
        else:
            return None

    def get_status(self, object):
        plan_status = PlanStatus.objects.filter(plan_classes_uid=object.plan_classes_uid).last()
        if plan_status:
            return plan_status.status
        else:
            return None

    class Meta:
        model = ProductClassesPlan
        # fields = (
        #     'id', 'equip_name', 'plan_classes_uid', 'sn', 'stage_product_batch_no', 'begin_time', 'end_time', 'classes',
        #     'plan_trains', 'actual_trains', 'operation_user', 'status', 'day_time', 'group')

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
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).all()
        for p_obj in p_status:
            if p_obj.status != '等待':
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
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).all()
        for p_obj in p_status:
            if p_obj.status != '等待':
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
    '''修改车次'''
    trains = serializers.IntegerField(write_only=True, help_text='修改车次')

    class Meta:
        model = ProductClassesPlan
        fields = ('trains',)
        read_only_fields = COMMON_READ_ONLY_FIELDS

    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).all()
        for p_obj in p_status:
            if p_obj.status != '运行中':
                raise serializers.ValidationError({'trains': '只有运行中的计划才可以修改车次'})
        trains = validated_data.get('trains')
        instance.plan_trains = trains
        instance.save()
        return instance
