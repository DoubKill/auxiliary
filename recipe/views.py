# Create your views here.
import json

import requests
from django.db.models import Prefetch, Max
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
from mes.settings import MES_URL
from production.models import MaterialTankStatus, PlanStatus
from recipe.filters import MaterialFilter, ProductInfoFilter, ProductBatchingFilter, \
    MaterialAttributeFilter
from recipe.serializers import MaterialSerializer, ProductInfoSerializer, \
    ProductBatchingListSerializer, ProductBatchingCreateSerializer, MaterialAttributeSerializer, \
    ProductBatchingRetrieveSerializer, ProductBatchingUpdateSerializer, \
    ProductBatchingPartialUpdateSerializer, ProductBatchingDetailUploadSerializer, ProductProcessSerializer, \
    ProductProcessDetailSerializer
from recipe.models import Material, ProductInfo, ProductBatching, MaterialAttribute, \
    ProductBatchingDetail, BaseAction, BaseCondition, ProductProcessDetail, MaterialSupplier


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
        if instance.use_flag is True and ProductBatchingDetail.objects.filter(material=instance,
                                                                              delete_flag=False).exists():
            raise ValidationError('该原材料已关联配方，无法停用!')
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
        stage_product_batch_no = self.request.query_params.get('stage_product_batch_no')
        if stage_product_batch_no:
            # 验证特殊配方
            try:
                equip_id = int(equip)
            except Exception:
                raise ValidationError('参数错误')
            if ProductBatching.objects.exclude(used_type=6).filter(
                    equip_id=equip_id,
                    stage_product_batch_no=stage_product_batch_no,
                    factory__isnull=True).exists():
                raise ValidationError('已存在相同机台的配方，请修改后重试！')
            return Response('ok')
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
    permission_classes = (IsAuthenticated,)

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
                'factory_id', 'site_id', 'product_info_id', 'precept', 'versions',
                'stage_id', 'last_updated_date', 'is_synced', 'is_changed', 'last_updated_user__username'
            )
        else:
            return self.queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('distinct'):
            data = set(queryset.values_list('stage_product_batch_no', flat=True))
            return Response({'results': data})
        if self.request.query_params.get('all'):
            recipe_no = self.request.query_params.get('recipe_no')
            if recipe_no:
                queryset = queryset.filter(stage_product_batch_no=recipe_no)
            data = queryset.values('id',
                                   'stage_product_batch_no',
                                   'batching_weight',
                                   'production_time_interval',
                                   'used_type')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

    # def get_permissions(self):
    #     if self.request.query_params.get('all'):
    #         return ()
    #     elif self.action == 'partial_update':
    #         return (IsAuthenticated(),
    #                 ProductBatchingPermissions())
    #     else:
    #         return (IsAuthenticated(),
    #                 PermissionClass(return_permission_params(self.model_name))())

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

    def perform_destroy(self, instance):
        if instance.used_type == 4:  # 停用
            if instance.equip:
                max_ids = PlanStatus.objects.filter(
                    product_no=instance.stage_product_batch_no,
                    equip_no=instance.equip.equip_no).values(
                    'plan_classes_uid').annotate(max_id=Max('id')).values_list('max_id', flat=True)
                exist_status = set(PlanStatus.objects.filter(id__in=max_ids).values_list('status', flat=True))
                if exist_status & {'已下达', '运行中'}:
                    raise ValidationError('该配方生产计划已下达或在运行中，无法停用！')
            instance.used_type = 7
        elif instance.used_type == 7:  # 启用
            instance.used_type = 4
        instance.last_updated_user = self.request.user
        instance.save()


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
        data = []
        material_data = MaterialTankStatus.objects.filter(
            equip_no=equip_no, tank_type=tank_type).values('material_no', 'tank_no', 'tank_name', 'provenance',
                                                           'material_name')
        for item in material_data:
            material = Material.objects.filter(material_no=item['material_no']).first()
            if not material:
                material = Material.objects.filter(material_name=item['material_name']).last()
            if not material:
                continue
            item['id'] = material.id
            item['material_name'] = material.material_name
            data.append(item)
        return Response(data={'results': data})


@method_decorator([api_recorder], name="dispatch")
class MaterialSupplierView(APIView):
    """根据原材料获取产地信息, 参数：?material_no=原材料编码"""

    def get(self, request):
        material_no = self.request.query_params.get('material_no')
        if not material_no:
            raise ValidationError('缺失参数')
        return Response(MaterialSupplier.objects.filter(
            material__material_no=material_no).values_list('provenance', flat=True))


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingIssue(APIView):

    def post(self, request):
        product_batching_id = self.request.data.get('product_batching_id')
        try:
            product_batching = ProductBatching.objects.get(id=product_batching_id)
        except Exception:
            raise ValidationError('object does not exist!')
        # if product_batching.is_synced:
        #     raise ValidationError('非法操作，该配方已同步至MES！')
        if product_batching.used_type != 4:
            raise ValidationError('非法操作，该配方未启用！')
        batching_data = ProductBatching.objects.filter(id=product_batching_id).values(
            'factory__global_no', 'site__global_no', 'product_info__product_no',
            'stage_product_batch_no', 'dev_type__category_no', 'stage__global_no',
            'versions', 'used_type'
        )
        data = batching_data[0]
        # data['batching_details'] = list(product_batching.batching_details.exclude(
        #     material__material_name='卸料').filter(delete_flag=0).values(
        #     'sn', 'material__material_no', 'actual_weight', 'standard_error', 'auto_flag', 'type'))
        batching_details = product_batching.batching_details.exclude(material__material_name='卸料').filter(delete_flag=0)
        data['batching_details'] = ProductBatchingDetailUploadSerializer(instance=batching_details, many=True).data
        ret = requests.post(MES_URL+'api/v1/recipe/product-dev-batching-receive/', json=data)
        if ret.status_code != 200:
            raise ValidationError('配方上传至MES失败：{}'.format(ret.text))
        else:
            ProductBatching.objects.filter(stage_product_batch_no=product_batching.stage_product_batch_no,
                                           dev_type=product_batching.dev_type).update(is_synced=1, is_changed=0)
        return Response('上传成功！')


class DevTypeProductBatching(APIView):

    def get(self, request):
        dev_type = self.request.query_params.get('dev_type')
        product_no = self.request.query_params.get('product_no')
        if not all([dev_type, product_no]):
            raise ValidationError('参数不足')
        query_params = {'dev_type': dev_type,
                        'product_no': product_no}
        try:
            ret = requests.get(MES_URL + 'api/v1/recipe/dev-type-batching/', params=query_params)
        except Exception:
            raise ValidationError('MES服务错误！')
        return Response(json.loads(ret.text))


@method_decorator([api_recorder], name="dispatch")
class ProductTechParams(APIView):

    def get(self, request):
        equip_id = self.request.query_params.get('equip_id')
        recipe_no = self.request.query_params.get('recipe_no')
        if not all([equip_id, recipe_no]):
            raise ValidationError('参数缺失！')
        pb = ProductBatching.objects.exclude(
            used_type=6).filter(equip_id=equip_id, batching_type=1, stage_product_batch_no=recipe_no).first()
        if not pb:
            return Response({})
        else:
            if hasattr(pb, 'processes'):
                process_data = ProductProcessSerializer(instance=pb.processes).data
            else:
                process_data = {}
            process_detail_data = ProductProcessDetailSerializer(instance=pb.process_details.filter(delete_flag=False).order_by('sn'), many=True).data
            return Response({'process_data': process_data, 'process_detail_data': process_detail_data})


@method_decorator([api_recorder], name="dispatch")
class BatchingMaterials(APIView):

    def get(self, request):
        query_set = ProductBatching.objects.all()
        product_no = self.request.query_params.get('product_no')
        if product_no:
            query_set = query_set.filter(stage_product_batch_no__icontains=product_no)
        return Response(query_set.values('stage_product_batch_no').distinct())