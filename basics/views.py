from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, mixins
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from basics.filters import EquipFilter, GlobalCodeTypeFilter, WorkScheduleFilter, GlobalCodeFilter, EquipCategoryFilter
from basics.models import GlobalCodeType, GlobalCode, WorkSchedule, Equip, SysbaseEquipLevel, \
    WorkSchedulePlan, ClassesDetail, PlanSchedule, EquipCategoryAttribute
from basics.serializers import GlobalCodeTypeSerializer, GlobalCodeSerializer, WorkScheduleSerializer, \
    EquipSerializer, SysbaseEquipLevelSerializer, WorkSchedulePlanSerializer, WorkScheduleUpdateSerializer, \
    ClassesDetailSerializer, PlanScheduleSerializer, EquipCategoryAttributeSerializer, ClassesSimpleSerializer
from mes.common_code import return_permission_params, CommonDeleteMixin
from mes.derorators import api_recorder
from mes.permissions import PermissionClass
from mes.paginations import SinglePageNumberPagination


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeTypeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码类型列表
    create:
        创建公共代码类型
    update:
        修改公共代码类型
    destroy:
        删除公共代码类型
    """
    queryset = GlobalCodeType.objects.filter(delete_flag=False)
    serializer_class = GlobalCodeTypeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = GlobalCodeTypeFilter

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.global_codes.filter().update(delete_flag=True, delete_user=request.user)
        return super().destroy(request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        公共代码列表
    create:
        创建公共代码
    update:
        修改公共代码
    destroy:
        删除公共代码
    """
    queryset = GlobalCode.objects.filter(delete_flag=False)
    serializer_class = GlobalCodeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    pagination_class = SinglePageNumberPagination
    filter_class = GlobalCodeFilter


@method_decorator([api_recorder], name="dispatch")
class WorkScheduleViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        工作日程列表
    create:
        创建工作日程
    update:
        修改工作日程
    destroy:
        删除工作日程
    """
    queryset = WorkSchedule.objects.filter(delete_flag=False)
    serializer_class = WorkScheduleSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = WorkScheduleFilter

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return WorkScheduleUpdateSerializer
        else:
            return WorkScheduleSerializer


@method_decorator([api_recorder], name="dispatch")
class EquipCategoryViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备种类列表
    create:
        创建设备种类
    update:
        修改设备种类
    destroy:
        删除设备种类
    """
    queryset = EquipCategoryAttribute.objects.filter(delete_flag=False)
    serializer_class = EquipCategoryAttributeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipCategoryFilter


@method_decorator([api_recorder], name="dispatch")
class EquipViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备列表
    create:
        创建设备
    update:
        修改设备
    destroy:
        删除设备
    """
    queryset = Equip.objects.filter(delete_flag=False)
    serializer_class = EquipSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = EquipFilter


@method_decorator([api_recorder], name="dispatch")
class SysbaseEquipLevelViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        设备层次列表
    create:
        创建设备层次
    update:
        修改设备层次
    destroy:
        删除设备层次
    """
    queryset = SysbaseEquipLevel.objects.filter(delete_flag=False)
    serializer_class = SysbaseEquipLevelSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class WorkSchedulePlanViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        工作日程计划列表
    create:
        创建工作日程计划
    update:
        修改工作日程计划
    destroy:
        删除工作日程计划
    """
    queryset = WorkSchedulePlan.objects.filter(delete_flag=False)
    serializer_class = WorkSchedulePlanSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))


@method_decorator([api_recorder], name="dispatch")
class ClassesDetailViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    """
    list:
        班次条目列表
    """
    queryset = ClassesDetail.objects.filter(delete_flag=False)
    serializer_class = ClassesSimpleSerializer
    model_name = queryset.model.__name__.lower()
    pagination_class = None
    permission_classes = (IsAuthenticatedOrReadOnly,)


@method_decorator([api_recorder], name="dispatch")
class PlanScheduleViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        计划时间列表
    create:
        创建计划时间
    update:
        修改计划时间
    destroy:
        删除计划时间
    """
    queryset = PlanSchedule.objects.filter()
    serializer_class = PlanScheduleSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,
                          PermissionClass(permission_required=return_permission_params(model_name)))

    @atomic()
    def create(self, request, *args, **kwargs):
        body = request.data
        for plan in body:
            serializer = self.get_serializer(data=plan)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response({"message": "create success"}, status=status.HTTP_201_CREATED)
