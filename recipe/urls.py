from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe.views import MaterialViewSet, ProductInfoViewSet, \
    ProductBatchingViewSet, MaterialAttributeViewSet, \
    ValidateProductVersionsView, ActionListView, ConditionListView, \
    RecipeObsoleteAPiView, BatchingEquip, TankMaterialVIew, MaterialSupplierView, ProductBatchingIssue, \
    DevTypeProductBatching, ProductTechParams, RecipeChangeHistoryViewSet

router = DefaultRouter()

# 原材料
router.register(r'materials', MaterialViewSet)

# 原材料属性
router.register(r'materials-attribute', MaterialAttributeViewSet)

# 胶料工艺信息
router.register(r'product-infos', ProductInfoViewSet)

# 胶料配料
router.register(r'product-batching', ProductBatchingViewSet)

router.register(r'recipe-change-history', RecipeChangeHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('batching-equips/', BatchingEquip.as_view()),
    path('recipe-obsolete/', RecipeObsoleteAPiView.as_view()),
    path('actions/', ActionListView.as_view()),
    path('conditions/', ConditionListView.as_view()),
    path('validate-versions/', ValidateProductVersionsView.as_view()),  # 验证版本号，创建胶料工艺信息前调用
    path('tank_materials/', TankMaterialVIew.as_view()),
    path('material_suppliers/', MaterialSupplierView.as_view()),
    path('product-batching-issue/', ProductBatchingIssue.as_view()),
    path('dev-type-batching/', DevTypeProductBatching.as_view()),
    path('product-tech-params/', ProductTechParams.as_view())
]
