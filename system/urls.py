from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token

from system.views import UserViewSet, UserGroupsViewSet, GroupExtensionViewSet, SectionViewSet, PermissionViewSet, \
    GroupAddUserViewSet, SystemConfigViewSet, ChildSystemInfoViewSet, LoginView, Synchronization, UpdatePassWord

# app_name = 'system'
router = DefaultRouter()

router.register(r"personnels_groups", UserGroupsViewSet)

router.register(r'personnels', UserViewSet)

router.register(r'group_extension', GroupExtensionViewSet)

router.register(r'section', SectionViewSet)

router.register(r"permission", PermissionViewSet)
# 系统配置
router.register(r"system-config", SystemConfigViewSet)
# 子系统信息
router.register(r"child-systems", ChildSystemInfoViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view()),
    path('group_add_user/<pk>/', GroupAddUserViewSet.as_view()),
    path('api-token-auth/', obtain_jwt_token),
    path('api-token-refresh/', refresh_jwt_token),
    path('synchronization/', Synchronization.as_view()),  # mes和上辅机同步接口
    path('update-password/', UpdatePassWord.as_view()),  # 修改密码接口
]
