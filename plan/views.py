from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
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

# Create your views here.
from recipe.models import Material, ProductProcess, ProductBatchingDetail, ProductProcessDetail
from work_station.api import IssueWorkStation
from work_station.models import IfdownShengchanjihua1, IfdownPmtRecipe1, IfdownRecipeCb1, IfdownRecipeOil11, \
    IfdownRecipePloy1, IfdownRecipeMix1
from production.models import PlanStatus, TrainsFeedbacks
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

    def plan_recipe_integrity_check(self, pcp_obj):
        # 检验计计划配方是否可用
        if not pcp_obj:
            raise ValidationError("无对应班次计划")
        try:
            product_batching = pcp_obj.product_day_plan.product_batching
        except:
            raise ValidationError("无对应日计划胶料配料标准")
        # 胶料配料详情，一份胶料对应多个配料
        product_batching_details = product_batching.batching_details.filter(delete_flag=False)
        if not product_batching_details:
            raise ValidationError("胶料配料详情为空，该计划不可用")
        product_process = ProductProcess.objects.filter(product_batching=product_batching).first()
        if not product_process:
            raise ValidationError("胶料配料步序为空，该计划不可用")
        # 步序详情，一份通用步序对应多份步序详情
        product_process_details = product_process.process_details.filter(delete_flag=False)
        if not product_process_details:
            raise ValidationError("胶料配料步序详情为空，该计划不可用")

        return product_batching, product_batching_details, product_process, product_process_details, pcp_obj

    def _map_PmtRecipe(self, pcp_object, product_process, product_batching):
        data = {
            "id": product_process.id,
            "lasttime": str(pcp_object.product_day_plan.plan_schedule.day_time),
            "oper": self.request.user.username,
            "recipe_code": product_batching.stage_product_batch_no,
            "recipe_name": product_batching.stage_product_batch_no,
            "equip_code": product_process.equip_code,
            "reuse_time": product_process.reuse_time,
            "mini_time": product_process.mini_time,
            "max_time": product_process.max_time,
            "mini_temp": product_process.mini_temp,
            "max_temp": product_process.max_temp,
            "over_temp": product_process.over_temp,
            "if_not": 1 if product_process.reuse_flag else 0,
            "temp_zz": product_process.zz_temp,
            "temp_xlm": product_process.xlm_temp,
            "temp_cb": product_process.cb_temp,
            "tempuse": 1 if product_process.temp_use_flag else 0,
            "usenot": 1 if product_process.use_flag else 0,
            "recstatus": "等待",
        }
        return data

    def _map_RecipeCb(self, product_batching, product_batching_details):
        datas = []
        product_batching_details = product_batching_details.filter(material__material_type__global_name="炭黑")
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": pbd.actual_weight,
                "error_allow": pbd.standard_error,
                "recipe_name": product_batching.stage_product_batch_no,
                "act_code": 1 if pbd.auto_flag else 0,  # ?
                "type": "",  # ?
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipeOil1(self, product_batching, product_batching_details):
        datas = []
        product_batching_details = product_batching_details.filter(material__material_type__global_name="油料")
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": pbd.actual_weight,
                "error_allow": pbd.standard_error,
                "recipe_name": product_batching.stage_product_batch_no,
                "act_code": 1 if pbd.auto_flag else 0,  # ?
                "type": "",  # ?
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipePloy(self, product_batching, product_batching_details):
        datas = []
        product_batching_details = product_batching_details.filter(material__material_type__global_name="胶料")
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": pbd.actual_weight,
                "error_allow": pbd.standard_error,
                "recipe_name": product_batching.stage_product_batch_no,
                "act_code": 1 if pbd.auto_flag else 0,  # ?
                "type": "",  # ?
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipeMix(self, product_batching, product_process_details):
        datas = []
        for ppd in product_process_details:
            data = {
                "id": ppd.id,
                "set_condition": ppd.condition.condition,  # ? 条件名称还是条件代码
                "set_time": int(ppd.time),
                "set_temp": int(ppd.temperature),
                "set_ener": ppd.energy,
                "set_power": ppd.power,
                "act_code": ppd.action.code,
                "set_pres": int(ppd.pressure),
                "set_rota": ppd.rpm,
                "recipe_name": product_batching.stage_product_batch_no,
                "recstatus": "等待",
            }
            datas.append(data)
        return datas

    def _map_Shengchanjihua(self, params, pcp_obj):
        data = {
            'id': pcp_obj.id,  # id
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
            'remark': '1',  # 计划单条下发默认值为1      c 创建,  u 更新 ,  d 删除 / 在炭黑表里表示增删改  计划表里用于标注批量计划的顺序
            'recstatus': '等待',  # 等待， 进行中， 完成
        }
        return data

    def _sync(self, args, params=None, ext_str=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe).issue_to_db()
        RecipeCb = self._map_RecipeCb(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeCb' + ext_str, RecipeCb).batch_to_db()
        RecipeOil1 = self._map_RecipeOil1(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeOil1' + ext_str, RecipeOil1).batch_to_db()
        RecipePloy = self._map_RecipePloy(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipePloy' + ext_str, RecipePloy).batch_to_db()
        RecipeMix = self._map_RecipeMix(product_batching, product_process_details)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix).batch_to_db()
        Shengchanjihua = self._map_Shengchanjihua(params, pcp_obj)
        IssueWorkStation('IfdownShengchanjihua' + ext_str, Shengchanjihua).issue_to_db()

    def _sync_update(self, args, params=None, ext_str=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe).update_to_db()
        RecipeCb = self._map_RecipeCb(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeCb' + ext_str, RecipeCb).batch_update_to_db()
        RecipeOil1 = self._map_RecipeOil1(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeOil1' + ext_str, RecipeOil1).batch_update_to_db()
        RecipePloy = self._map_RecipePloy(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipePloy' + ext_str, RecipePloy).batch_update_to_db()
        RecipeMix = self._map_RecipeMix(product_batching, product_process_details)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix).batch_update_to_db()
        # 重传逻辑不需要修改计划
        # Shengchanjihua = self._map_Shengchanjihua(params, pcp_obj)
        # IssueWorkStation('IfdownShengchanjihua'+ext_str, Shengchanjihua).update_to_db()

    @atomic()
    def post(self, request):
        params = request.data
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()

        """
        # 通过id去取相关数据
        params = {}
        params['stage_product_batch_no'] = pcp_obj.product_day_plan.product_batching.stage_product_batch_no
        params['day_time'] = pcp_obj.product_day_plan.plan_schedule.day_time
        params['plan_classes_uid'] = pcp_obj.plan_classes_uid
        params['begin_time'] = pcp_obj.work_schedule_plan.start_time
        params['end_time'] = pcp_obj.work_schedule_plan.end_time
        params['classes'] = pcp_obj.work_schedule_plan.classes.global_name
        params['group'] = pcp_obj.work_schedule_plan.group.global_name
        params['plan_trains'] = pcp_obj.plan_trains
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).last()
        if tfb_obj:
            params['actual_trains'] = tfb_obj.actual_trains
            params['operation_user'] = tfb_obj.operation_user
        else:
            params['actual_trains'] = None
            params['operation_user'] = None
        """
        # 校验计划与配方完整性

        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        equip_no = ps_obj.equip_no
        if "0" in equip_no:
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        if ps_obj.status != '等待':
            return Response({'_': "只有等待中的计划才能下达！"}, status=400)
        self._sync(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str)
        # 模型类的名称需根据设备编号来拼接
        ps_obj.status = '运行中'
        ps_obj.save()
        return Response({'_': '下达成功'}, status=200)

    @atomic()
    def put(self, request):
        params = request.data
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()
        # 校验计划与配方完整性

        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).first()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        equip_no = ps_obj.equip_no
        if "0" in equip_no:
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        if ps_obj.status != '运行中':
            return Response({'_': "只有运行中的计划才能下达！"}, status=400)
        self._sync_update(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str)
        # 模型类的名称需根据设备编号来拼接
        # 重传默认不修改plan_status
        # ps_obj.status = '运行'
        # ps_obj.save()
        return Response({'_': '重传成功'}, status=200)


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
    # permission_classes = ()
    # authentication_classes = ()
    permission_classes = (IsAuthenticated,)
    serializer_class = PlanReceiveSerializer
    queryset = ProductDayPlan.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
