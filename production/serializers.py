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

from recipe.models import ProductBatching
from work_station.models import IfupReportBasis, IfupReportWeight, IfupReportMix, IfupReportCurve


class EquipStatusSerializer(BaseModelSerializer):
    """机台状况反馈"""

    class Meta:
        model = EquipStatus
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class TrainsFeedbacksSerializer(BaseModelSerializer):
    """车次产出反馈"""
    equip_status = serializers.SerializerMethodField(read_only=True)
    production_details = serializers.SerializerMethodField(read_only=True)

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

    def get_production_details(self, object):
        production_details = {}
        irb_obj = IfupReportBasis.objects.filter(机台号=object.equip_no, 计划号=object.plan_classes_uid,
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
            group = product.classes_detail.work_schedule_plan.all().first()
            return group.group_name if group else None
        else:
            return None

    class Meta:
        model = PalletFeedbacks
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialTankStatusSerializer(BaseModelSerializer):
    """称量参数"""

    class Meta:
        model = MaterialTankStatus
        fields = (
        "id", "equip_no", "tank_type", "tank_name", "masterial_name", "low_value", "advance_value", "adjust_value",
        "dot_time",
        "fast_speed",
        "low_speed", "used_flag")
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MaterialStatisticsSerializer(BaseModelSerializer):
    """物料统计报表"""

    class Meta:
        model = ExpendMaterial
        fields = "__all__"
        read_only_fields = COMMON_READ_ONLY_FIELDS


class EquipStatusPlanSerializer(BaseModelSerializer):
    """主页面展示"""
    status = serializers.SerializerMethodField(read_only=True, help_text='机台状态')
    product_no = serializers.SerializerMethodField(read_only=True, help_text='当前胶料编码')
    group_name_list = serializers.SerializerMethodField(read_only=True, help_text='班组列表')
    current_trains = serializers.SerializerMethodField(read_only=True, help_text='收皮数量')
    # equip = serializers.

    def get_status(self, object):
        es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()  # 因为机台状况反馈是不断新增数据的，所以直接找最后一条
        if es_obj:
            return es_obj.status
        else:
            return None

    def get_current_trains(self, object):
        es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()  # 因为机台状况反馈是不断新增数据的，所以直接找最后一条
        if es_obj:
            return es_obj.current_trains
        else:
            return None

    def get_product_no(self, object):
        pfb_obj = TrainsFeedbacks.objects.filter(equip_no=object.equip_no).last()
        if pfb_obj:
            return pfb_obj.product_no
        else:
            return None

    def get_group_name_list(self, object):
        res = GlobalCode.objects.annotate(
            plan_sum=Sum(
                'work_schedule_plan__plan_schedule__ps_day_plan__pdp_product_classes_plan__plan_trains')).filter(
            global_type__type_name="班组",
            work_schedule_plan__plan_schedule__ps_day_plan__equip=object).values('plan_sum', 'global_name')
        for i in res:
            ppcp_queryset = ProductClassesPlan.objects.filter(
                product_day_plan__plan_schedule__work_schedule_plan__group__global_name=i['global_name']).values(
                'plan_classes_uid')
            uid_list = []
            for ppcp_obj in ppcp_queryset:
                uid_list.append(ppcp_obj['plan_classes_uid'])
            trains_sum = 0
            for uid in uid_list:
                tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=uid).last()  # 因为车次反馈是不断新增数据的，所以直接找最后一条
                trains_sum += tfb_obj.actual_trains
            i['actual_trains'] = trains_sum
        return res

    class Meta:
        model = Equip
        fields = ('id', 'equip_no', 'status', 'current_trains', 'product_no', 'group_name_list')


class EquipDetailedSerializer(BaseModelSerializer):
    """主页面详情展示"""
    status = serializers.SerializerMethodField(read_only=True, help_text='机台状态')
    current_trains = serializers.SerializerMethodField(read_only=True, help_text='收皮数量')
    product_no = serializers.SerializerMethodField(read_only=True, help_text='当前胶料编码')
    group_name = serializers.SerializerMethodField(read_only=True, help_text='当前班组')
    group_product = serializers.SerializerMethodField(read_only=True, help_text='班组对应胶料列表')
    statusinfo = serializers.SerializerMethodField(read_only=True, help_text='机台状态统计')

    def get_status(self, object):
        es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()  # 因为机台状况反馈是不断新增数据的，所以直接找最后一条
        if es_obj:
            return es_obj.status
        else:
            return None

    def get_current_trains(self, object):
        es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()  # 因为机台状况反馈是不断新增数据的，所以直接找最后一条
        if es_obj:
            return es_obj.current_trains
        else:
            return None

    def get_product_no(self, object):
        pfb_obj = TrainsFeedbacks.objects.filter(equip_no=object.equip_no).last()
        if pfb_obj:
            return pfb_obj.product_no
        else:
            return None

    def get_group_name(self, object):
        es_obj = EquipStatus.objects.filter(equip_no=object.equip_no).last()
        if es_obj:
            pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=es_obj.plan_classes_uid).first()
            classes_detail = pcp_obj.classes_detail
            plan_schedule = pcp_obj.product_day_plan.plan_schedule
            wsp_obj = WorkSchedulePlan.objects.filter(classes_detail=classes_detail,
                                                      plan_schedule=plan_schedule).first()
            if wsp_obj:
                return wsp_obj.group_name
            else:
                return None
        else:
            return None

    def get_group_product(self, object):
        if self.get_group_name(object):
            res = ProductBatching.objects.annotate(
                sum_trains=Sum('pb_day_plan__pdp_product_classes_plan__plan_trains')).filter(
                pb_day_plan__equip__equip_no=object.equip_no,
                pb_day_plan__plan_schedule__work_schedule_plan__group_name=self.get_group_name(
                    object)).values('sum_trains', 'pb_day_plan__product_batching__stage_product_batch_no')
            for i in res:
                pcp_queryset = ProductClassesPlan.objects.filter(
                    product_day_plan__product_batching__stage_product_batch_no=i[
                        'pb_day_plan__product_batching__stage_product_batch_no'])
                uid_List = []
                for pcp_obj in pcp_queryset:
                    uid_List.append(pcp_obj.plan_classes_uid)
                sum_trains = 0
                for uid in uid_List:
                    tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=uid).last()
                    sum_trains += tfb_obj.actual_trains
                i['trains_plan'] = sum_trains
            return res
        else:
            return None

    def get_statusinfo(self, object):
        es_list = EquipStatus.objects.filter(equip_no=object.equip_no).values('status').distinct()
        for es_dict in es_list:
            es_dict['num'] = EquipStatus.objects.filter(equip_no=object.equip_no, status=es_dict['status']).count()
        return es_list

    class Meta:
        model = Equip
        fields = (
            'id', 'equip_no', 'status', 'current_trains', 'product_no', 'group_name', 'group_product', 'statusinfo')


class WeighInformationSerializer(BaseModelSerializer):
    """称量信息"""
    weigh_info = serializers.SerializerMethodField(read_only=True)

    def get_weigh_info(self, object):
        weigh_info = []
        irw_queryset = IfupReportWeight.objects.filter(机台号=object.equip_no, 计划号=object.plan_classes_uid.hex,
                                                       配方号=object.product_no).all()
        print(irw_queryset)
        if irw_queryset:
            for irw_obj in irw_queryset:
                weigh_dict = {}
                weigh_dict['id'] = irw_obj.序号
                weigh_dict['物料名称'] = irw_obj.物料名称
                weigh_dict['设定重量'] = irw_obj.设定重量
                weigh_dict['实际重量'] = irw_obj.实际重量
                weigh_dict['秤状态'] = irw_obj.秤状态
                weigh_dict['物料类型'] = irw_obj.物料类型
                weigh_info.append(weigh_dict)
            return weigh_info
        else:
            return None

    class Meta:
        model = TrainsFeedbacks
        fields = ('weigh_info',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class MixerInformationSerializer(BaseModelSerializer):
    """密炼信息"""
    mixer_info = serializers.SerializerMethodField(read_only=True)

    def get_mixer_info(self, object):
        mixer_info = []
        irm_queryset = IfupReportMix.objects.filter(机台号=object.equip_no, 计划号=object.plan_classes_uid.hex,
                                                    配方号=object.product_no).all()
        if irm_queryset:
            for irm_obj in irm_queryset:
                mixer_dict = {}
                mixer_dict['id'] = irm_obj.序号
                mixer_dict['条件'] = irm_obj.条件
                mixer_dict['时间'] = irm_obj.时间
                mixer_dict['温度'] = irm_obj.温度
                mixer_dict['功率'] = irm_obj.功率
                mixer_dict['能量'] = irm_obj.能量
                mixer_dict['动作'] = irm_obj.动作
                mixer_dict['转速'] = irm_obj.转速
                mixer_dict['压力'] = irm_obj.压力
                mixer_info.append(mixer_dict)
            return mixer_info
        else:
            return None

    class Meta:
        model = TrainsFeedbacks
        fields = ('mixer_info',)
        read_only_fields = COMMON_READ_ONLY_FIELDS


class CurveInformationSerializer(BaseModelSerializer):
    """工艺曲线信息"""
    curve_info = serializers.SerializerMethodField(read_only=True)

    def get_curve_info(self, object):
        curve_info = []
        irc_queryset = IfupReportCurve.objects.filter(机台号=object.equip_no, 计划号=object.plan_classes_uid.hex,
                                                      配方号=object.product_no).all()
        if irc_queryset:
            for irc_obj in irc_queryset:
                curve_dict = {}
                curve_dict['id'] = irc_obj.序号
                curve_dict['温度'] = irc_obj.温度
                curve_dict['功率'] = irc_obj.功率
                curve_dict['转速'] = irc_obj.转速
                curve_dict['压力'] = irc_obj.压力
                curve_dict['时间'] = irc_obj.存盘时间
                curve_info.append(curve_dict)
            return curve_info
        else:
            return None

    class Meta:
        model = TrainsFeedbacks
        fields = ('curve_info',)
        read_only_fields = COMMON_READ_ONLY_FIELDS
