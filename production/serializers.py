import datetime
from rest_framework import serializers
from basics.models import Equip, WorkSchedulePlan, GlobalCode
from mes.base_serializer import BaseModelSerializer
from mes.conf import COMMON_READ_ONLY_FIELDS
from plan.models import ProductClassesPlan, ProductDayPlan
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, ExpendMaterial, QualityControl, \
    OperationLog, MaterialTankStatus
from django.db.models import Sum
from django.forms.models import model_to_dict
from production.utils import strtoint
from recipe.models import ProductBatching, Material
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

    # production_details = serializers.SerializerMethodField(read_only=True)
    # status = serializers.SerializerMethodField(read_only=True)

    def get_equip_status(self, object):
        equip_status = {}
        plan_classes_uid = object.plan_classes_uid
        equip_no = object.equip_no
        equip = EquipStatus.objects.filter(plan_classes_uid=plan_classes_uid, equip_no=equip_no).first()
        if not equip:
            raise serializers.ValidationError("该车次数据无对应设备，请检查相关设备")
        equip_status.update(temperature=equip.temperature,
                            energy=equip.energy,
                            rpm=equip.rpm)
        return equip_status

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
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PlanStatusSerializer(BaseModelSerializer):
    """计划状态变更"""

    class Meta:
        model = PlanStatus
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ExpendMaterialSerializer(BaseModelSerializer):
    """原材料消耗表"""

    class Meta:
        model = ExpendMaterial
        fields = "__all__"
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
        tfb_obj = Material.objects.filter(material_no=obj.material_no).first()
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
            "low_speed", "use_flag")
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


class WeighInformationSerializer(serializers.ModelSerializer):
    """称量信息"""

    class Meta:
        model = IfupReportWeightBackups
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MixerInformationSerializer(serializers.ModelSerializer):
    """密炼信息"""

    class Meta:
        model = IfupReportMixBackups
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class CurveInformationSerializer(serializers.ModelSerializer):
    """工艺曲线信息"""

    class Meta:
        model = EquipStatus
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS
