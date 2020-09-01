from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework import mixins, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from basics.views import CommonDeleteMixin
from mes.derorators import api_recorder
from plan.filters import ProductDayPlanFilter, PalletFeedbacksFilter
from plan.serializers import UpRegulationSerializer, DownRegulationSerializer, UpdateTrainsSerializer, \
    PalletFeedbacksPlanSerializer, PlanReceiveSerializer, ProductDayPlanSerializer
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded
from rest_framework.views import APIView

from production.models import PlanStatus
from work_station.api import IssueWorkStation


@method_decorator([api_recorder], name="dispatch")
class ProductDayPlanViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        胶料日计划列表
    create:
        新建胶料日计划（单增），暂且不用，
    update:
        修改原胶料日计划
    destroy:
        删除胶料日计划
    """
    queryset = ProductDayPlan.objects.filter(delete_flag=False).select_related(
        'equip__category', 'plan_schedule', 'product_batching').prefetch_related(
        'pdp_product_classes_plan__work_schedule_plan', 'pdp_product_batching_day_plan')
    serializer_class = ProductDayPlanSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = ProductDayPlanFilter
    ordering_fields = ['id', 'equip__category__equip_type__global_name']

    def destroy(self, request, *args, **kwargs):
        """"胶料计划删除 先删除胶料计划，随后删除胶料计划对应的班次日计划和原材料需求量表"""
        instance = self.get_object()
        MaterialDemanded.objects.filter(
            product_classes_plan__product_day_plan=instance).delete()
        ProductClassesPlan.objects.filter(product_day_plan=instance).update(delete_flag=True, delete_user=request.user)
        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class ProductDayPlanManyCreate(APIView):
    """胶料计划群增接口"""
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        if isinstance(request.data, dict):
            many = False
        elif isinstance(request.data, list):
            many = True
        else:
            return Response(data={'detail': '数据有误'}, status=400)
        s = ProductDayPlanSerializer(data=request.data, many=many, context={'request': request})
        s.is_valid(raise_exception=True)
        s.save()
        return Response('新建成功')


@method_decorator([api_recorder], name="dispatch")
class PalletFeedbackViewSet(mixins.ListModelMixin,
                            GenericViewSet, CommonDeleteMixin):
    """
    list:
        计划管理展示
    delete:
        计划管理删除
    """
    queryset = ProductClassesPlan.objects.filter(delete_flag=False).order_by('sn')
    serializer_class = PalletFeedbacksPlanSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = PalletFeedbacksFilter

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        plan_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).last()
        if plan_status.status != '等待':
            return Response({'_': "只有等待的计划才能删除"}, status=400)
        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator([api_recorder], name="dispatch")
class UpRegulation(GenericViewSet, mixins.UpdateModelMixin):
    """上调"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = UpRegulationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


@method_decorator([api_recorder], name="dispatch")
class DownRegulation(GenericViewSet, mixins.UpdateModelMixin):
    """下调"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = DownRegulationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


@method_decorator([api_recorder], name="dispatch")
class UpdateTrains(GenericViewSet, mixins.UpdateModelMixin):
    """修改车次"""
    queryset = ProductClassesPlan.objects.filter(delete_flag=False)
    serializer_class = UpdateTrainsSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)


@method_decorator([api_recorder], name="dispatch")
class StopPlan(APIView):
    """计划停止"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id")
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        equip_name = params.get("equip_name")
        pcp_obj = ProductClassesPlan.objects.filter(id=plan_id).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        if ps_obj.status != '运行中':
            return Response({'_': "只有运行中的计划才能停止！"}, status=400)
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

        return Response({'_': '修改成功'}, status=200)


@method_decorator([api_recorder], name="dispatch")
class IssuedPlan(APIView):
    """下达计划"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        equip_name = params.get("equip_name", None)
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        if ps_obj.status != '等待':
            return Response({'_': "只有等待中的计划才能下达！"}, status=400)
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
            'remark': 'c',
            'recstatus': '运行中',
        }
        temp = IssueWorkStation('IfdownShengchanjihua1', temp_data)
        temp.issue_to_db()

        return Response({'_': '修改成功'}, status=200)


@method_decorator([api_recorder], name="dispatch")
class RetransmissionPlan(APIView):
    """重传计划"""

    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id")
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        equip_name = params.get("equip_name")
        pcp_obj = ProductClassesPlan.objects.filter(id=plan_id).first()
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).last()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        if ps_obj.status != '等待':
            return Response({'_': "只有等待中的计划才能运行！"}, status=400)
        ps_obj.status = '运行中'
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

        return Response({'_': '修改成功'}, status=200)


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
