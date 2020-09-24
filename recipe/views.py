# Create your views here.
from django.db.models import Prefetch
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from basics.models import Equip
from basics.views import CommonDeleteMixin
from mes.common_code import return_permission_params
from mes.derorators import api_recorder
from mes.permissions import PermissionClass, ProductBatchingPermissions
from production.models import MaterialTankStatus
from recipe.filters import MaterialFilter, ProductInfoFilter, ProductBatchingFilter, \
    MaterialAttributeFilter
from recipe.serializers import MaterialSerializer, ProductInfoSerializer, \
    ProductBatchingListSerializer, ProductBatchingCreateSerializer, MaterialAttributeSerializer, \
    ProductBatchingRetrieveSerializer, ProductBatchingUpdateSerializer, \
    ProductBatchingPartialUpdateSerializer
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
            raise ValidationError('该原材料已关联配方，无法停用')
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
    """验证配方信息是否存在，参数：xxx/?site=SITEid&product_info=胶料代码id&versions=版本号&equip=设备id&stage=段次id"""

    def get(self, request):
        site = self.request.query_params.get('site')
        product_info = self.request.query_params.get('product_info')
        versions = self.request.query_params.get('versions')
        equip = self.request.query_params.get('equip')
        stage = self.request.query_params.get('stage')
        if not all([versions, site, product_info, equip, stage]):
            raise ValidationError('参数不足')
        try:
            site = int(site)
            product_info = int(product_info)
            equip_id = int(equip)
            stage = int(stage)
        except Exception:
            raise ValidationError('参数错误')
        if ProductBatching.objects.exclude(used_type=6).filter(
                equip_id=equip_id,
                site_id=site,
                versions=versions,
                product_info_id=product_info,
                stage_id=stage).exists():
            raise ValidationError('已存在相同机台的配方，请修改后重试！')
        return Response('ok')


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
            return ProductBatching.objects.exclude(
                used_type=6).filter(delete_flag=False).order_by('-created_date').values(
                'id', 'stage_product_batch_no', 'product_info__product_name',
                'equip__equip_name', 'equip__equip_no', 'dev_type__category_name',
                'used_type', 'batching_weight', 'production_time_interval',
                'stage__global_name', 'site__global_name', 'processes__sp_num',
                'created_date', 'created_user__username', 'batching_type', 'dev_type_id',
                'equip__category__category_name', 'submit_user__username', 'reject_user__username',
                'used_user__username', 'obsolete_user__username', 'equip_id',
                'factory_id', 'site_id', 'product_info_id', 'precept', 'versions', 'stage_id'
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
class RecipeObsoleteAPiView(APIView):
    """
    接收MES弃用配方接口
    """

    def post(self, request):
        stage_product_batch_no = self.request.data.get('stage_product_batch_no')
        dev_type = self.request.data.get('dev_type')
        product_batching = ProductBatching.objects.exclude(used_type=6).filter(
            stage_product_batch_no=stage_product_batch_no,
            dev_type__category_no=dev_type,
            batching_type=2).first()
        if not product_batching:
            return Response('暂无该配方数据', status=status.HTTP_200_OK)
        product_batching.used_type = 6
        product_batching.save()
        return Response('弃用成功', status=status.HTTP_200_OK)


@method_decorator([api_recorder], name="dispatch")
class BatchingEquip(APIView):

    def get(self, request):
        dev_type = self.request.query_params.get('dev_type')
        try:
            dev_type = int(dev_type)
        except Exception:
            raise ValidationError('参数错误')
        equip_data = Equip.objects.filter(category_id=dev_type).values('id', 'equip_no', 'equip_name',
                                                                       'category__category_name')
        return Response(data={'results': equip_data})


@method_decorator([api_recorder], name="dispatch")
class TankMaterialVIew(APIView):
    """炭黑、油料罐原材料数据，参数：tank_type=(1:炭黑，2:油料)&equip_no="""

    def get(self, request):
        tank_type = self.request.query_params.get('tank_type')
        equip_no = self.request.query_params.get('equip_no')
        if not all([tank_type, equip_no]):
            raise ValidationError('参数不足')
        if tank_type not in ['1', '2']:
            raise ValidationError('参数错误')
        mat_nos = set(MaterialTankStatus.objects.filter(equip_no=equip_no,
                                                        tank_type=tank_type).values_list('material_no', flat=True))
        data = Material.objects.filter(material_no__in=mat_nos).values('id', 'material_name', 'material_no')
        return Response(data={'results': data})
