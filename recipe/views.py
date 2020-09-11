# Create your views here.
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from basics.models import Equip
from basics.views import CommonDeleteMixin
from mes.common_code import return_permission_params
from mes.derorators import api_recorder
from mes.permissions import PermissionClass, ProductBatchingPermissions
from recipe.filters import MaterialFilter, ProductInfoFilter, ProductBatchingFilter, \
    MaterialAttributeFilter
from recipe.serializers import MaterialSerializer, ProductInfoSerializer, \
    ProductBatchingListSerializer, ProductBatchingCreateSerializer, MaterialAttributeSerializer, \
    ProductBatchingRetrieveSerializer, ProductBatchingUpdateSerializer, \
    ProductBatchingPartialUpdateSerializer, RecipeReceiveSerializer
from recipe.models import Material, ProductInfo, ProductBatching, MaterialAttribute, \
    ProductBatchingDetail, BaseAction, BaseCondition, ProductProcessDetail


@method_decorator([api_recorder], name="dispatch")
class MaterialViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        原材料列表
    create:
        新建原材料
    update:
        修改原材料
    destroy:
        删除原材料
    """
    queryset = Material.objects.filter(delete_flag=False).select_related('material_type').order_by('-created_date')
    serializer_class = MaterialSerializer
    model_name = queryset.model.__name__.lower()
    filter_backends = (DjangoFilterBackend,)
    filter_class = MaterialFilter

    def get_permissions(self):
        if self.request.query_params.get('all'):
            return ()
        else:
            return (IsAuthenticated(),
                    PermissionClass(return_permission_params(self.model_name))())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.filter(use_flag=1).values('id', 'material_no',
                                                      'material_name', 'material_type__global_name')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if ProductBatchingDetail.objects.filter(material=instance).exists():
            raise ValidationError('该原材料已关联配方，无法删除')
        else:
            return super().destroy(request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class MaterialAttributeViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        原材料属性列表
    create:
        新建原材料属性
    update:
        修改原材料属性
    destroy:
        删除原材料属性
    """
    queryset = MaterialAttribute.objects.filter(delete_flag=False).order_by('-created_date')
    serializer_class = MaterialAttributeSerializer
    model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticated, PermissionClass(return_permission_params(model_name)))
    filter_backends = (DjangoFilterBackend,)
    filter_class = MaterialAttributeFilter


@method_decorator([api_recorder], name="dispatch")
class ValidateProductVersionsView(APIView):
    """验证版本号，创建胶料工艺信息前调用，参数：xxx/?factory=产地id&site=SITEid&product_info=胶料代码id&versions=版本号"""

    def get(self, request):
        factory = self.request.query_params.get('factory')
        site = self.request.query_params.get('site')
        product_info = self.request.query_params.get('product_info')
        versions = self.request.query_params.get('versions')
        if not all([versions, factory, site, product_info]):
            raise ValidationError('参数不足')
        try:
            site = int(site)
            product_info = int(product_info)
            factory = int(factory)
        except Exception:
            raise ValidationError('参数错误')
        product_batching = ProductBatching.objects.filter(factory_id=factory, site_id=site,
                                                          product_info_id=product_info
                                                          ).order_by('-versions').first()
        if product_batching:
            if product_batching.versions >= versions:  # TODO 目前版本检测根据字符串做比较，后期搞清楚具体怎样填写版本号
                return Response({'code': -1, 'message': '版本号不得小于现有版本号'})
        return Response({'code': 0, 'message': ''})


@method_decorator([api_recorder], name="dispatch")
class ProductInfoViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """
    list:
        胶料代码列表
    retrieve:
        胶料代码标准详情
    create:
        新建胶料代码
    update:
        修改胶料代码
    partial_update:
        修改胶料代码
    """
    queryset = ProductInfo.objects.filter(delete_flag=False).order_by('-created_date')
    serializer_class = ProductInfoSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProductInfoFilter
    model_name = queryset.model.__name__.lower()

    def get_permissions(self):
        if self.request.query_params.get('all'):
            return ()
        else:
            return (IsAuthenticated(),
                    PermissionClass(return_permission_params(self.model_name))())

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'product_no', 'product_name')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingViewSet(ModelViewSet):
    """
    list:
        胶料配料标准列表
    retrieve:
        胶料配料标准详情
    create:
        新建胶料配料标准
    update:
        配料
    partial_update:
        配料审批
    """
    queryset = ProductBatching.objects.filter(
        delete_flag=False).select_related("equip__category", "product_info"
                                          ).prefetch_related(
                                            Prefetch('process_details',
                                                     queryset=ProductProcessDetail.objects.filter(
                                                         delete_flag=False).select_related('condition', 'action')),
                                            Prefetch('batching_details',
                                                     queryset=ProductBatchingDetail.objects.filter(
                                                         delete_flag=False).select_related('material__material_type'))
                                            ).order_by('-created_date')
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProductBatchingFilter
    model_name = queryset.model.__name__.lower()

    def get_queryset(self):
        if self.action == 'list':
            return ProductBatching.objects.filter(delete_flag=False, used_type__in=(1, 2, 4)
                                                  ).order_by('-created_date').values(
                'id', 'stage_product_batch_no', 'product_info__product_name',
                'equip__equip_name', 'equip__equip_no', 'dev_type__category_name',
                'used_type', 'batching_weight', 'production_time_interval',
                'stage__global_name', 'site__global_name', 'processes__sp_num',
                'created_date', 'created_user__username', 'batching_type', 'dev_type_id',
                'equip__category__category_name'
            )
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('distinct'):
            data = set(queryset.values_list('stage_product_batch_no', flat=True))
            return Response({'results': data})
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'stage_product_batch_no', 'batching_weight', 'production_time_interval')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

    def get_permissions(self):
        if self.request.query_params.get('all'):
            return ()
        elif self.action == 'partial_update':
            return (IsAuthenticated(),
                    ProductBatchingPermissions())
        else:
            return (IsAuthenticated(),
                    PermissionClass(return_permission_params(self.model_name))())

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductBatchingListSerializer
        elif self.action == 'create':
            return ProductBatchingCreateSerializer
        elif self.action == 'retrieve':
            return ProductBatchingRetrieveSerializer
        elif self.action == 'partial_update':
            return ProductBatchingPartialUpdateSerializer
        else:
            return ProductBatchingUpdateSerializer


@method_decorator([api_recorder], name="dispatch")
class ActionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = BaseAction.objects.values('id', 'code', 'action')
        return Response({'results': data})


@method_decorator([api_recorder], name="dispatch")
class ConditionListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = BaseCondition.objects.values('id', 'code', 'condition')
        return Response({'results': data})


@method_decorator([api_recorder], name="dispatch")
class RecipeReceiveAPiView(CreateAPIView):
    """
    接受上辅机配方数据接口
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RecipeReceiveSerializer
    queryset = ProductBatching.objects.all()


@method_decorator([api_recorder], name="dispatch")
class RecipeObsoleteAPiView(APIView):
    """
    接收MES弃用配方接口
    """

    def post(self, request):
        stage_product_batch_no = self.request.data.get('stage_product_batch_no')
        try:
            product_batching = ProductBatching.objects.get(stage_product_batch_no=stage_product_batch_no)
        except ProductBatching.DoesNotExist:
            return Response('暂无该配方数据', status=status.HTTP_200_OK)
        product_batching.used_type = 6
        product_batching.save()
        return Response('弃用成功', status=status.HTTP_200_OK)


@method_decorator([api_recorder], name="dispatch")
class BatchingEquip(APIView):
    """复制配方时根据机型id获取还未配料的机台"""

    def get(self, request):
        dev_type = self.request.query_params.get('dev_type')
        try:
            dev_type = int(dev_type)
        except Exception:
            raise ValidationError('参数错误')
        existed_equips = list(ProductBatching.objects.filter(dev_type=dev_type, used_type__in=(1, 2, 4)).values_list('equip_id', flat=True))
        equip_data = Equip.objects.exclude(
            id__in=existed_equips).filter(category_id=dev_type).values('id', 'equip_no', 'equip_name',
                                                                       'category__category_name')
        return Response(data={'results': equip_data})