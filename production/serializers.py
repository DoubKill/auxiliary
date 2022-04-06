import datetime

from django.db.transaction import atomic
from rest_framework import serializers
from basics.models import Equip, WorkSchedulePlan, GlobalCode
from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from plan.models import ProductClassesPlan, ProductDayPlan
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, ExpendMaterial, QualityControl, \
    OperationLog, MaterialTankStatus, ProcessFeedback, AlarmLog
from django.db.models import Sum, Q
from django.forms.models import model_to_dict
from production.utils import strtoint
from recipe.models import ProductBatching, Material, ProductProcessDetail
from production.models import IfupReportBasisBackups, IfupReportWeightBackups, IfupReportMixBackups, \
    IfupReportCurveBackups
from django.db.models import Sum, Max


class EquipStatusSerializer(BaseModelSerializer):
    """机台状况反馈"""

    class Meta:
        model = EquipStatus
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class TrainsFeedbacksSerializer(BaseModelSerializer):
    """车次产出反馈"""
    equip_status = serializers.SerializerMethodField(read_only=True)
    actual_weight = serializers.SerializerMethodField(read_only=True)

    # production_details = serializers.SerializerMethodField(read_only=True)
    # status = serializers.SerializerMethodField(read_only=True)

    def get_equip_status(self, object):
        equip_status = {}
        plan_classes_uid = object.plan_classes_uid
        equip_no = object.equip_no
        current_trains = object.actual_trains
        equip = EquipStatus.objects.filter(plan_classes_uid=plan_classes_uid, equip_no=equip_no,
                                           current_trains=current_trains).last()
        if equip:
            # raise serializers.ValidationError("该车次数据无对应设备，请检查相关设备")
            equip_status.update(temperature=equip.temperature,
                                energy=equip.energy,
                                rpm=equip.rpm)
        return equip_status

    def get_actual_weight(self, object):
        actual = object.actual_weight
        if actual:
            if len(str(actual)) >= 5:
                return str(actual / 100)
        return str(actual)

    '''
    # zqf 这些是在原有的基础上加的 随后我重新写了接口 这些就没用了 暂时注释掉
    def get_production_details(self, object):
        production_details = {}
        irb_obj = IfupReportBasisBackups.objects.filter(机台号=strtoint(object.equip_no), 计划号=object.plan_classes_uid,
                                                 配方号=object.product_no).order_by('存盘时间').last()
        if irb_obj:
            production_details['控制方式'] = irb_obj.控制方式  # 本远控
            production_details['作业方式'] = irb_obj.作业方式  # 手自动
            production_details['总重量'] = irb_obj.总重量
            production_details['排胶时间'] = irb_obj.排胶时间
            production_details['排胶温度'] = irb_obj.排胶温度
            production_details['排胶能量'] = irb_obj.排胶能量
            production_details['员工代号'] = irb_obj.员工代号
            production_details['存盘时间'] = irb_obj.存盘时间
            production_details['间隔时间'] = irb_obj.间隔时间
            production_details['密炼时间'] = irb_obj.存盘时间  # 暂时由存盘时间代替 后期需要确实是否是存盘时间-开始时间
            return production_details
        else:
            return None

    def get_status(self, object):
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=object.plan_classes_uid).last()
        if ps_obj:
            return ps_obj.status
        return None
    '''

    class Meta:
        model = TrainsFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class TrainsFeedbacksUpSerializer(BaseModelSerializer):
    """车次产出反馈上传"""

    factory_date = serializers.SerializerMethodField(read_only=True)

    def get_factory_date(self, object):
        plan_uid = object.plan_classes_uid
        pcp = ProductClassesPlan.objects.filter(plan_classes_uid=plan_uid).first()
        if pcp:
            date = pcp.work_schedule_plan.plan_schedule.day_time
        else:
            date = datetime.date.today()
        return str(date)

    class Meta:
        model = TrainsFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PalletFeedbacksUpSerializer(BaseModelSerializer):
    """托盘产出反馈"""

    factory_date = serializers.SerializerMethodField(read_only=True)

    def get_factory_date(self, object):
        plan_uid = object.plan_classes_uid
        pcp = ProductClassesPlan.objects.filter(plan_classes_uid=plan_uid).first()
        if pcp:
            date = pcp.work_schedule_plan.plan_schedule.day_time
        else:
            date = datetime.date.today()
        return str(date)

    class Meta:
        model = PalletFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PalletFeedbacksSerializer(BaseModelSerializer):
    """托盘产出反馈"""
    stage = serializers.SerializerMethodField(read_only=True)

    def get_stage(self, object):
        plan_classes_uid = object.plan_classes_uid if object.plan_classes_uid else 0
        productclassesplan = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid).first()
        if productclassesplan:
            try:
                stage = productclassesplan.product_day_plan.product_batching.stage.global_name
            except:
                stage = None
        else:
            stage = None
        return stage if stage else ""

    class Meta:
        model = PalletFeedbacks
        exclude = ("created_date", "last_updated_date", "delete_date", "delete_flag",
                   "created_user", "last_updated_user", "delete_user")
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PalletSerializer(BaseModelSerializer):
    """托盘产出反馈"""

    class Meta:
        model = PalletFeedbacks
        exclude = ("created_date", "last_updated_date", "delete_date", "delete_flag",
                   "created_user", "last_updated_user", "delete_user")
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PlanStatusSerializer(BaseModelSerializer):
    """计划状态变更"""

    class Meta:
        model = PlanStatus
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS

    def create(self, validated_data):
        uid = validated_data.get("plan_classes_uid")
        pcp = ProductClassesPlan.objects.filter(plan_classes_uid=uid).last()
        if pcp:
            pcp.status = "完成"
            pcp.save()
        return super().create(validated_data)


class ExpendMaterialSerializer(BaseModelSerializer):
    """原材料消耗表"""

    class Meta:
        model = ExpendMaterial
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ExpendMaterialSerializer2(BaseModelSerializer):
    """原材料消耗表"""
    material_type = serializers.SerializerMethodField()

    def get_material_type(self, obj):
        material_type_dict = self.context['material_type_dict']
        return material_type_dict.get(obj.get('material_no'), obj.get('material_type'))

    class Meta:
        model = ExpendMaterial
        fields = ('equip_no', 'product_no', 'material_type', 'material_no', 'material_name', 'actual_weight')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class OperationLogSerializer(BaseModelSerializer):
    """操作日志"""

    class Meta:
        model = OperationLog
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class QualityControlSerializer(BaseModelSerializer):
    """质检结果表"""

    class Meta:
        model = QualityControl
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductionRecordSerializer(BaseModelSerializer):
    """密炼生产履历"""
    validtime = serializers.SerializerMethodField(read_only=True)
    class_group = serializers.SerializerMethodField(read_only=True)
    margin = serializers.CharField(default=None, read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_status(self, object):
        plan_status = PlanStatus.objects.filter(plan_classes_uid=object.plan_classes_uid, equip_no=object.equip_no,
                                                product_no=object.product_no).first()
        if plan_status:
            return plan_status.status
        else:
            return None

    def get_validtime(self, object):
        end_time = object.end_time if object.end_time else 0
        validtime = end_time + datetime.timedelta(days=1)
        return validtime if validtime else ""

    def get_class_group(self, object):
        product = ProductClassesPlan.objects.filter(plan_classes_uid=object.plan_classes_uid).first()
        if product:
            group = product.work_schedule_plan.group
            return group.global_name if group else None
        else:
            return None

    class Meta:
        model = PalletFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialTankStatusSerializer(BaseModelSerializer):
    """称量参数"""
    material_name1 = serializers.SerializerMethodField(read_only=True, help_text='原材料名称')

    def get_material_name1(self, obj):
        tfb_obj = Material.objects.filter(material_name=obj.material_name, use_flag=True).last()
        if tfb_obj:
            return tfb_obj.material_name
        else:
            return None

    class Meta:
        model = MaterialTankStatus
        fields = (
            "id", "material_name1", "material_no", "equip_no", "tank_type", "tank_name", "low_value",
            "advance_value",
            "adjust_value",
            "dot_time",
            "fast_speed",
            "low_speed", "use_flag", 'provenance')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialStatisticsSerializer(BaseModelSerializer):
    """物料统计报表"""

    class Meta:
        model = ExpendMaterial
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


# class EquipDetailedSerializer(BaseModelSerializer):
#     """主页面详情展示"""
#     status_current_trains = serializers.SerializerMethodField(read_only=True, help_text='机台状态和收皮数量')
#     product_no_classes = serializers.SerializerMethodField(read_only=True, help_text='当前胶料编码和当前班次')
#     group_product = serializers.SerializerMethodField(read_only=True, help_text='班次对应胶料列表')
#     statusinfo = serializers.SerializerMethodField(read_only=True, help_text='机台状态统计')
#
#     def get_status_current_trains(self, object):
#         es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()  # 因为机台状况反馈是不断新增数据的，所以直接找最后一条
#         if es_obj:
#             # return es_obj.status
#             return {"status": es_obj.status, "current_trains": es_obj.current_trains}
#         else:
#             return None
#
#     def get_product_no_classes(self, object):
#         pfb_obj = TrainsFeedbacks.objects.filter(equip_no=object.equip_no).last()
#         if pfb_obj:
#             # return pfb_obj.product_no
#             return {"product_no": pfb_obj.product_no, "classes": pfb_obj.classes}
#         else:
#             return None
#
#     def get_group_product(self, object):
#         pfb_obj = TrainsFeedbacks.objects.filter(equip_no=object.equip_no).last()
#         if pfb_obj:
#             res = ProductBatching.objects.annotate(
#                 sum_trains=Sum('pb_day_plan__pdp_product_classes_plan__plan_trains')).filter(
#                 pb_day_plan__equip__equip_no=object.equip_no,
#                 pb_day_plan__pdp_product_classes_plan__work_schedule_plan__classes__global_name=pfb_obj.classes).values(
#                 'sum_trains', 'pb_day_plan__product_batching__stage_product_batch_no')
#             for i in res:
#                 pcp_queryset = ProductClassesPlan.objects.filter(
#                     product_day_plan__product_batching__stage_product_batch_no=i[
#                         'pb_day_plan__product_batching__stage_product_batch_no'])
#                 uid_List = []
#                 for pcp_obj in pcp_queryset:
#                     uid_List.append(pcp_obj.plan_classes_uid)
#                 sum_trains = 0
#                 for uid in uid_List:
#                     tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=uid).last()
#                     if tfb_obj:
#                         sum_trains += tfb_obj.actual_trains
#                 i['trains_plan'] = sum_trains
#             return res
#         else:
#             return None
#
#     def get_statusinfo(self, object):
#         es_list = EquipStatus.objects.filter(equip_no=object.equip_no).values('status').distinct()
#         for es_dict in es_list:
#             es_dict['num'] = EquipStatus.objects.filter(equip_no=object.equip_no, status=es_dict['status']).count()
#         return es_list
#
#     class Meta:
#         model = Equip
#         fields = (
#             'id', 'equip_no', 'status_current_trains', 'product_no_classes', 'group_product', 'statusinfo')

class WeighInformationSerializer1(serializers.ModelSerializer):
    """称量信息"""

    class Meta:
        model = IfupReportWeightBackups
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class WeighInformationSerializer2(serializers.ModelSerializer):
    """称量信息"""

    class Meta:
        model = ExpendMaterial
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MixerInformationSerializer1(serializers.ModelSerializer):
    """密炼信息"""

    class Meta:
        model = IfupReportMixBackups
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MixerInformationSerializer2(serializers.ModelSerializer):
    """密炼信息"""

    class Meta:
        model = ProcessFeedback
        fields = "__all__"


class CurveInformationSerializer(serializers.ModelSerializer):
    """工艺曲线信息"""

    class Meta:
        model = EquipStatus
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class TrainsFeedbacksSerializer2(BaseModelSerializer):
    """车次产出反馈"""
    status = serializers.SerializerMethodField(read_only=True)
    actual_weight = serializers.SerializerMethodField(read_only=True)
    mixer_time = serializers.SerializerMethodField(read_only=True)
    ai_value = serializers.SerializerMethodField(read_only=True)

    def get_ai_value(self, obj):
        irm_queryset = ProcessFeedback.objects.filter(
            Q(plan_classes_uid=obj.plan_classes_uid,
              equip_no=obj.equip_no,
              product_no=obj.product_no,
              current_trains=obj.actual_trains)
            &
            ~Q(Q(condition='') | Q(condition__isnull=True))
        ).order_by('-sn').first()
        if irm_queryset:
            return irm_queryset.power
        return None

    def to_representation(self, instance):
        data = super(TrainsFeedbacksSerializer2, self).to_representation(instance)
        evacuation_energy = data['evacuation_energy']
        equip_no = data['equip_no']
        actual_weight = data['actual_weight']
        try:
            if equip_no == 'Z01':
                data['evacuation_energy'] = int(evacuation_energy / 10)
            if equip_no == 'Z02':
                data['evacuation_energy'] = int(evacuation_energy / 0.6)
            if equip_no == 'Z04':
                data['evacuation_energy'] = int(evacuation_energy * 0.28 * float(actual_weight) / 1000)
            if equip_no == 'Z12':
                data['evacuation_energy'] = int(evacuation_energy / 5.3)
            if equip_no == 'Z13':
                data['evacuation_energy'] = int(evacuation_energy / 31.7)
        except Exception:
            pass
        return data

    def get_mixer_time(self, obj):
        try:
            return obj.end_time - obj.begin_time
        except:
            return None

    def get_actual_weight(self, obj):
        if not obj.actual_weight:
            return None
        else:
            return str(obj.actual_weight / 100)

    def get_status(self, object):
        ps_obj = PlanStatus.objects.filter(equip_no=object.equip_no,
                                           plan_classes_uid=object.plan_classes_uid,
                                           product_no=object.product_no,
                                           actual_trains=object.actual_trains).order_by(
            'product_time').last()
        if ps_obj:
            status = ps_obj.status
        else:
            status = None
        return status

    class Meta:
        model = TrainsFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProcessFeedbackSerializer(BaseModelSerializer):
    """步序反馈报表"""

    class Meta:
        model = ProcessFeedback
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class AlarmLogSerializer(BaseModelSerializer):
    """步序反馈报表"""

    class Meta:
        model = AlarmLog
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS
