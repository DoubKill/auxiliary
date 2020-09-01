from rest_framework.routers import DefaultRouter
from django.urls import path, include
from plan.views import PalletFeedbackViewSet, UpRegulation, DownRegulation, \
    UpdateTrains, StopPlan, IssuedPlan, RetransmissionPlan, PlanReceive, ProductDayPlanViewSet, ProductDayPlanManyCreate

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

urlpatterns = [
    path('', include(router.urls)),
    path('product-day-plan-manycreate/', ProductDayPlanManyCreate.as_view()),  # 群增胶料日计划
    path('stop-plan/', StopPlan.as_view()),  # 计划停止
    path('issued-plan/', IssuedPlan.as_view()),  # 计划下达
    path('retransmission-plan/', RetransmissionPlan.as_view()),  # 计划重传
    path('plan-receive/', PlanReceive.as_view()),  # mes下达到上辅机
]