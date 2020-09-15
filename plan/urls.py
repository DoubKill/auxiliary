from django.urls import path, include
from rest_framework.routers import DefaultRouter

from plan.views import PalletFeedbackViewSet, UpRegulation, DownRegulation, \
    UpdateTrains, StopPlan, IssuedPlan, PlanReceive, ProductDayPlanViewSet, ProductDayPlanManyCreate, PlanStatusList, \
    ProductClassesPlanManyCreate, ProductClassesPlanList

router = DefaultRouter()

# 胶料日计划
router.register(r'product-day-plans', ProductDayPlanViewSet)
# 计划管理展示删除
router.register(r'pallet-feed-backs', PalletFeedbackViewSet)
# 上调
router.register(r'up-regulation', UpRegulation)
# 下调
router.register(r'down-regulation', DownRegulation)
# 修改车次
router.register(r'update-trains', UpdateTrains)
# 计划管理新增页面展示
# router.register(r'product-classes-plan-list', ProductClassesPlanList)

urlpatterns = [
    path('', include(router.urls)),
    path('product-day-plan-manycreate/', ProductDayPlanManyCreate.as_view()),  # 群增胶料日计划
    # path('product-classes-plan-manycreate/', ProductClassesPlanManyCreate.as_view()),  # 群增胶料日班次计划以及单删
    path('stop-plan/', StopPlan.as_view()),  # 计划停止
    path('issued-plan/', IssuedPlan.as_view()),  # 计划下达
    # path('retransmission-plan/', RetransmissionPlan.as_view()),  # 计划重传，前端用的重传接口是计划下达的put方法，此接口暂时没用了
    path('plan-receive/', PlanReceive.as_view()),  # mes下达到上辅机
    path('plan-status-list/', PlanStatusList.as_view()),  # 计划管理当前机台计划展示
]
