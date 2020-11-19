from django.urls import path, include
from rest_framework.routers import DefaultRouter

from datain.views import GlobalCodeReceive, WorkScheduleReceive, ClassesDetailReceive, EquipCategoryAttributeReceive, \
    EquipReceive, PlanScheduleReceive, WorkSchedulePlanReceive, MaterialReceive, GlobalCodeTypeReceive, \
    ProductInfoReceive, RecipeReceiveAPiView, MaterialAttributeReceiveAPiView, MaterialSupplierReceiveAPiView

router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('global_code-receive/', GlobalCodeReceive.as_view()),  # 公共代码表
    path('work_schedule-receive/', WorkScheduleReceive.as_view()),  # 倒班管理
    path('classes_detail_receive/', ClassesDetailReceive.as_view()),  # 倒班条目
    path('equip_category_attribute_receive/', EquipCategoryAttributeReceive.as_view()),  # 设备种类属性
    path('equip_receive/', EquipReceive.as_view()),  # 设备
    path('plan_schedule_receive/', PlanScheduleReceive.as_view()),  # 排班管理
    path('work_schedule_plan_receive/', WorkSchedulePlanReceive.as_view()),  # 排班详情
    path('material_receive/', MaterialReceive.as_view()),  # 原材料
    path('global_code_type_receive/', GlobalCodeTypeReceive.as_view()),  # 公共代码类型
    path('product_info_receive/', ProductInfoReceive.as_view()),
    path('recipe-receive/', RecipeReceiveAPiView.as_view()),  # 接收mes下发的配方
    path('material_attr_receive/', MaterialAttributeReceiveAPiView.as_view()),  # 接收原材料属性
    path('material_supplier_receive/', MaterialSupplierReceiveAPiView.as_view()),  # 接收原材料供应商
]