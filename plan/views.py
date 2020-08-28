from django.db.transaction import atomic
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import mixins, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from basics.views import CommonDeleteMixin
from mes.derorators import api_recorder
from plan.filters import ProductDayPlanFilter, MaterialDemandedFilter, ProductBatchingDayPlanFilter, \
    PalletFeedbacksFilter
from plan.serializers import UpRegulationSerializer, DownRegulationSerializer, UpdateTrainsSerializer, \
    PalletFeedbacksPlanSerializer, PlanReceiveSerializer
#ProductDayPlanSerializer, MaterialDemandedSerializer, ProductBatchingDayPlanSerializer, ProductDayPlanCopySerializer, ProductBatchingDayPlanCopySerializer, MaterialRequisitionClassesSerializer, \
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, ProductBatchingDayPlan, \
    ProductBatchingClassesPlan, MaterialRequisitionClasses
from plan.paginations import LimitOffsetPagination
from rest_framework.views import APIView
from basics.models import Equip, PlanSchedule

# Create your views here.
from plan.uuidfield import UUidTools
from production.models import PalletFeedbacks, PlanStatus
from recipe.models import Material
from work_station.api import IssueWorkStation
from work_station.models import IfdownShengchanjihua1

'''
@method_decorator([api_recorder], name="dispatch")
class ProductDayPlanViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        胶料日计划列表
    create:
        新建胶料日计划
    update:
        修改原胶料日计划
    destroy:
        删除胶料日计划
    """
    queryset = ProductDayPlan.objects.filter(delete_flag=False)
    serializer_class = ProductDayPlanSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ProductDayPlanFilter
    ordering_fields = ['id', 'equip__category__equip_type__global_name']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for pcp_obj in instance.pdp_product_classes_plan.all():
            MaterialDemanded.objects.filter(
                plan_classes_uid=pcp_obj.plan_classes_uid).update(delete_flag=True,
                                                                  delete_user=request.user)
        ProductClassesPlan.objects.filter(product_day_plan=instance).update(delete_flag=True, delete_user=request.user)

        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class MaterialDemandedViewSet(ListAPIView):
    """
    list:
        原材料需求量列表
    """
    queryset = MaterialDemanded.objects.filter(delete_flag=False)
    serializer_class = MaterialDemandedSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = MaterialDemandedFilter


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingDayPlanViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        配料小料日计划列表
    create:
        新建配料小料日计划
    update:
        修改配料小料日计划
    destroy:
        删除配料小料日计划
    """
    queryset = ProductBatchingDayPlan.objects.filter(delete_flag=False)
    serializer_class = ProductBatchingDayPlanSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ProductBatchingDayPlanFilter
    ordering_fields = ['id', 'equip__category__equip_type__global_name']

    # pagination_class = LimitOffsetPagination

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        for pbcp_obj in instance.pdp_product_batching_classes_plan.all():
            MaterialDemanded.objects.filter(
                plan_classes_uid=pbcp_obj.plan_classes_uid).update(delete_flag=True,
                                                                   delete_user=request.user)
        ProductBatchingClassesPlan.objects.filter(product_batching_day_plan=instance).update(delete_flag=True,
                                                                                             delete_user=request.user)

        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingDayPlanManyCreate(APIView):
    def post(self, request, *args, **kwargs):
        if isinstance(request.data, dict):
            many = False
        elif isinstance(request.data, list):
            many = True
        else:
            return Response(data={'detail': '数据有误'}, status=400)
        pbdp_ser = ProductBatchingDayPlanSerializer(data=request.data, many=many, context={'request': request})
        pbdp_ser.is_valid(raise_exception=True)
        book_obj_or_list = pbdp_ser.save()
        return Response(ProductBatchingDayPlanSerializer(book_obj_or_list, many=many).data)


@method_decorator([api_recorder], name="dispatch")
class MaterialRequisitionClassesViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        领料日班次计划列表
    create:
        新建领料日班次计划
    update:
        修改领料日班次计划
    destroy:
        删除领料日班次计划
    """
    queryset = MaterialRequisitionClasses.objects.filter(delete_flag=False)
    serializer_class = MaterialRequisitionClassesSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)

    # pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(created_user=self.request.user, plan_classes_uid=UUidTools.uuid1_hex())

    def perform_update(self, serializer):
        serializer.save(last_updated_user=self.request.user)


@method_decorator([api_recorder], name="dispatch")
class MaterialDemandedAPIView(APIView):
    def get(self, request):
        filter_dict = {}
        if request.GET.get('plan_date', None):  # 日期
            plan_date = request.GET.get('plan_date')
            filter_dict['plan_schedule'] = PlanSchedule.objects.filter(day_time=plan_date).first()
        # material_type
        if request.GET.get('material_name', None):  # 原材料名称
            material_name = request.GET.get('material_name')
            filter_dict['material_demanded'] = Material.objects.filter(material_type__global_name=material_name).first()
        if request.GET.get('material_type', None):  # 公共代码GlobalCode原材料类别id
            material_type = request.GET.get('material_type')
            filter_dict['material'] = Material.objects.filter(material_type_id=material_type).first()
        if filter_dict:
            m_list = MaterialDemanded.objects.filter(**filter_dict).values('material', 'plan_schedule').distinct()
        else:
            m_list = MaterialDemanded.objects.filter().values('material', 'plan_schedule', ).distinct()
        response_list = []
        for m_dict in m_list:
            m_queryset = MaterialDemanded.objects.filter(material=m_dict['material'],
                                                         plan_schedule=m_dict['plan_schedule'])
            response_list.append(m_dict)
            md_obj = MaterialDemanded.objects.filter(material=m_dict['material']).first()
            response_list[-1]['material_type'] = md_obj.material.material_type.global_name
            response_list[-1]['material_no'] = md_obj.material.material_no
            response_list[-1]['material_name'] = md_obj.material.material_name
            response_list[-1]['md_material_requisition_classes'] = []
            for i in range(len(md_obj.md_material_requisition_classes.all())):
                dict_key = ['morning', 'afternoon', 'night']
                user_dict = {dict_key[i]: float(md_obj.md_material_requisition_classes.all()[i].weight)}
                response_list[-1]['md_material_requisition_classes'].append(user_dict)
            response_list[-1]['material_demanded_list'] = []
            i = 0
            for m_obj in m_queryset.values_list('id', 'material_demanded'):
                dict_key = ['id', 'material_demanded']
                user_dict = {}
                user_dict[dict_key[0]] = m_obj[0]
                user_dict[dict_key[1]] = m_obj[1]
                response_list[-1]['material_demanded_list'].append(user_dict)
                i += 1
        return JsonResponse(response_list, safe=False)


@method_decorator([api_recorder], name="dispatch")
class ProductDayPlanCopyView(CreateAPIView):
    """复制胶料日计划"""
    serializer_class = ProductDayPlanCopySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


@method_decorator([api_recorder], name="dispatch")
class ProductBatchingDayPlanCopyView(CreateAPIView):
    """复制配料小料日计划"""
    serializer_class = ProductBatchingDayPlanCopySerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)


@method_decorator([api_recorder], name="dispatch")
class ProductDayPlanManyCreate(APIView):
    """胶料计划群增接口"""

    def post(self, request, *args, **kwargs):
        if isinstance(request.data, dict):
            many = False
        elif isinstance(request.data, list):
            many = True
        else:
            return Response(data={'detail': '数据有误'}, status=400)
        pbdp_ser = ProductDayPlanSerializer(data=request.data, many=many, context={'request': request})
        pbdp_ser.is_valid(raise_exception=True)
        book_obj_or_list = pbdp_ser.save()
        return Response(ProductDayPlanSerializer(book_obj_or_list, many=many).data)

'''
@method_decorator([api_recorder], name="dispatch")
class PalletFeedbacksViewSet(mixins.ListModelMixin,
                             GenericViewSet, CommonDeleteMixin):
    """
    list:
        计划管理展示
    delete:
        计划管路删除
    """
    queryset = ProductClassesPlan.objects.filter(delete_flag=False).order_by('sn')
    serializer_class = PalletFeedbacksPlanSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = PalletFeedbacksFilter


class UpRegulation(GenericViewSet, mixins.UpdateModelMixin):
    """上调"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = UpRegulationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


class DownRegulation(GenericViewSet, mixins.UpdateModelMixin):
    """下调"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = DownRegulationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


class UpdateTrains(GenericViewSet, mixins.UpdateModelMixin):
    """修改车次"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = UpdateTrainsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


class StopPlan(APIView):
    """计划停止"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id")
        if plan_id is None:
            return Response("没有传id", status=400)
        equip_name = params.get("equip_name")
        pcp_obj = ProductClassesPlan.objects.filter(id=plan_id).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response("计划状态变更没有数据", status=400)
        if ps_obj.status != '运行中':
            return Response("只有运行中的计划才能停止！", status=400)
        ps_obj.status = '等待'
        ps_obj.save()

        temp_data = {
            'id': params.get("id", None),  # id
            'state': '等待',  # 计划状态：等待，运行中，完成
            'remark': 'u',
            'recstatus': '等待'
        }
        temp = IssueWorkStation('IfdownShengchanjihua1', temp_data)
        temp.issue_to_db()

        return Response('修改成功', status=200)


class IssuedPlan(APIView):
    """下达计划"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response("没有传id", status=400)
        equip_name = params.get("equip_name", None)
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response("计划状态变更没有数据", status=400)
        if ps_obj.status != '等待':
            return Response("只有等待中的计划才能运行！", status=400)
        ps_obj.status = '运行'
        ps_obj.save()

        temp_data = {
            # 'id': params.get("id", None),  # id
            'recipe': params.get("stage_product_batch_no", None),  # 配方名
            'recipeid': params.get("stage_product_batch_no", None),  # 配方编号
            'lasttime': params.get("day_time", None),  # 班日期
            'planid': params.get("plan_classes_uid", None),  # 计划编号  plan_no
            'startime': params.get("begin_time", None),  # 开始时间
            'stoptime': params.get("end_time", None),  # 结束时间
            'grouptime': params.get("classes", None),  # 班次
            'groupoper': params.get("group", None),  # 班组????
            'setno': params.get("plan_trains", None),  # 设定车次
            'actno': params.get("actual_trains", None),  # 当前车次
            'oper': params.get("operation_user", None),  # 操作员角色
            'state': '运行中',  # 计划状态：等待，运行中，完成
            'remark':'c',
            'recstatus': '运行中',
        }
        temp = IssueWorkStation('IfdownShengchanjihua1', temp_data)
        temp.issue_to_db()

        return Response('修改成功', status=200)


class RetransmissionPlan(APIView):
    """重传计划"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id")
        if plan_id is None:
            return Response("没有传id", status=400)
        equip_name = params.get("equip_name")
        pcp_obj = ProductClassesPlan.objects.filter(id=plan_id).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).last()
        if not ps_obj:
            return Response("计划状态变更没有数据", status=400)
        if ps_obj.status != '等待':
            return Response("只有等待中的计划才能运行！", status=400)
        ps_obj.status = '运行'
        ps_obj.save()

        temp_data = {
            'id': params.get("id", None),  # id
            'setno': params.get("plan_trains", None),  # 设定车次
            'state': '等待',  # 计划状态：等待，运行中，完成
            'remark': 'u',
            'recstatus': '更新完成'

        }
        temp = IssueWorkStation('IfdownShengchanjihua1', temp_data)
        temp.issue_to_db()

        return Response('修改成功', status=200)

@method_decorator([api_recorder], name="dispatch")
class PlanReceive(CreateAPIView):
    """
        接受上辅机计划数据接口
        """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PlanReceiveSerializer
    queryset = ProductDayPlan.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



