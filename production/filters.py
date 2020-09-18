import django_filters

from production.models import *


class TrainsFeedbacksFilter(django_filters.rest_framework.FilterSet):
    """车次产出反馈过滤器"""
    plan_classes_uid = django_filters.CharFilter(field_name='plan_classes_uid', help_text='班次计划唯一码')
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机号')
    product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料编号')
    operation_user = django_filters.CharFilter(field_name="operation_user", help_text="操作员")

    class Meta:
        model = TrainsFeedbacks
        fields = ('plan_classes_uid', 'equip_no', 'product_no', 'operation_user')


class PalletFeedbacksFilter(django_filters.rest_framework.FilterSet):
    """托盘产出反馈过滤器"""
    plan_classes_uid = django_filters.CharFilter(field_name='plan_classes_uid', help_text='班次计划唯一码')
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机号')
    product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料编号')
    st = django_filters.DateTimeFilter(field_name="end_time", help_text='生产时间', lookup_expr="gte")
    et = django_filters.DateTimeFilter(field_name="end_time", help_text='生产时间', lookup_expr="lte")
    classes = django_filters.CharFilter(field_name="classes", help_text='班次')

    class Meta:
        model = PalletFeedbacks
        fields = ('plan_classes_uid', 'equip_no', 'product_no', "classes", "pallet_no")


class EquipStatusFilter(django_filters.rest_framework.FilterSet):
    """机台状态反馈过滤器"""
    plan_classes_uid = django_filters.CharFilter(field_name='plan_classes_uid', help_text='班次计划唯一码')
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机号')
    st = django_filters.DateTimeFilter(field_name="product_time", help_text='生产时间', lookup_expr="gte")
    et = django_filters.DateTimeFilter(field_name="product_time", help_text='生产时间', lookup_expr="lte")

    # product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料编号')

    class Meta:
        model = EquipStatus
        fields = ('plan_classes_uid', 'current_trains')


class PlanStatusFilter(django_filters.rest_framework.FilterSet):
    """计划状态过滤器"""
    plan_classes_uid = django_filters.CharFilter(field_name='plan_classes_uid', help_text='班次计划唯一码')
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机号')
    product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料编号')

    class Meta:
        model = PlanStatus
        fields = ('plan_classes_uid', )


class ExpendMaterialFilter(django_filters.rest_framework.FilterSet):
    """原材料消耗过滤器"""
    st = django_filters.DateTimeFilter(field_name="product_time", help_text='开始时间', lookup_expr="gte")
    et = django_filters.DateTimeFilter(field_name="product_time", help_text='结束时间', lookup_expr="lte")
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机台号')
    product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料')
    material_type = django_filters.CharFilter(field_name='material_type', help_text='原材料类型')

    class Meta:
        model = ExpendMaterial
        fields = ('st', 'et', 'equip_no', 'product_no', 'material_type',)


class QualityControlFilter(django_filters.rest_framework.FilterSet):
    """质量检测结果过滤器"""
    barcode = django_filters.CharFilter(field_name='barcode', help_text='班次计划唯一码')

    class Meta:
        model = QualityControl
        fields = ('barcode',)


class WeighParameterCarbonFilter(django_filters.rest_framework.FilterSet):
    """称量过滤器"""
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机台号')

    class Meta:
        model = MaterialTankStatus
        fields = ('equip_no',)


class MaterialStatisticsFilter(django_filters.rest_framework.FilterSet):
    """物料统计报表过滤器"""
    st = django_filters.DateTimeFilter(field_name="product_time", help_text='开始时间', lookup_expr="gte")
    et = django_filters.DateTimeFilter(field_name="product_time", help_text='结束时间', lookup_expr="lte")
    equip_no = django_filters.CharFilter(field_name='equip_no', help_text='机台号')
    product_no = django_filters.CharFilter(field_name='product_no', help_text='产出胶料')
    material_type = django_filters.CharFilter(field_name='material_type', help_text='原材料类型')

    class Meta:
        model = ExpendMaterial
        fields = ('st', 'et', 'equip_no', 'product_no', 'material_type',)
