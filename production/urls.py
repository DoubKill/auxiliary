from django.urls import include, path
from rest_framework.routers import DefaultRouter

from production.views import TrainsFeedbacksViewSet, PalletFeedbacksViewSet, EquipStatusViewSet, PlanStatusViewSet, \
    ExpendMaterialViewSet, OperationLogViewSet, QualityControlViewSet, \
    ProductionRecordViewSet, PlanRealityViewSet, ProductActualViewSet, WeighParameterCarbonViewSet, \
    WeighParameterFuelViewSet, EquipStatusPlanList, EquipDetailedList, WeighInformationList, MixerInformationList, \
    CurveInformationList, MaterialStatisticsViewSet, TrainsFeedbacksAPIView

router = DefaultRouter()

# 车次/批次产出反馈
router.register(r'trains-feedbacks', TrainsFeedbacksViewSet)

# 托盘产出反馈
router.register(r'pallet-feedbacks', PalletFeedbacksViewSet)

# 机台状况反馈
router.register(r'equip-status', EquipStatusViewSet)

# 计划状态变更
router.register(r'plan-status', PlanStatusViewSet)

# 原材料消耗表
router.register(r'expend-materials', ExpendMaterialViewSet)

# 操作日志
router.register(r'operation-logs', OperationLogViewSet)

# 质检结果表
router.register(r'quality-control', QualityControlViewSet)

# 密炼LOT生产履历
router.register(r'production-record', ProductionRecordViewSet)

# 密炼实绩
router.register(r'plan-reality', PlanRealityViewSet, basename="plan-reality")

# 密炼机台别计划对比
router.register(r'product-actual', ProductActualViewSet, basename="product-actual")

# 称量参数
router.register(r'weigh-cb', WeighParameterCarbonViewSet, basename="weigh-cb")

router.register(r'weigh-oil', WeighParameterFuelViewSet, basename="weigh-oil")

# 物料统计
router.register(r'material-statistics', MaterialStatisticsViewSet, basename="material-statistics")

# 主页面展示
router.register(r'equip-status-plan-list', EquipStatusPlanList, basename="equip-status-plan-list")
# 主页面详情展示
router.register(r'equip-detailed-list', EquipDetailedList, basename="equip-detailed-list")
# 称量信息展示
router.register(r'weigh-information-list', WeighInformationList, basename="weigh-information-list")
# 密炼信息展示
router.register(r'mixer-information-list', MixerInformationList, basename="mixer-information-list")
# 工艺曲线信息展示
router.register(r'curve-information-list', CurveInformationList, basename="curve-information-list")
# 车次报表展示
router.register(r'trains-feedbacks-apiview', TrainsFeedbacksAPIView, basename="trains-feedbacks-apiview")

urlpatterns = [
    path('', include(router.urls)),
]
