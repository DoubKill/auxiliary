from django.db.models import Max
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

from basics.models import GlobalCode
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
from mes.common_code import WebService
from production.utils import strtoint
from collections import OrderedDict


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

    @atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        plan_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).order_by(
            'product_time').last()
        if plan_status.status != '等待':
            return Response({'_': "只有等待的计划才能删除"}, status=400)
        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        # 删除原材料需求量
        for md_obj in instance.m_product_classes_plan.all():
            md_obj.delete_flag = True
            md_obj.save()
        # 删除计划状态表
        plan_status.delete_flag = True
        plan_status.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanStatusList(APIView):
    """计划管理当前机台计划展示"""

    def get(self, request):
        params = request.query_params
        equip_no = params.get('equip_no')
        ps_obj = PlanStatus.objects.filter(equip_no=equip_no, status='运行中').first()
        plan_status_list = {}
        if not ps_obj:
            return Response({'results': plan_status_list}, 200)
        pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=ps_obj.plan_classes_uid).first()
        if not pcp_obj:
            return Response({'results': plan_status_list}, 200)
        plan_status_list['equip_no'] = equip_no
        plan_status_list['begin_time'] = pcp_obj.work_schedule_plan.start_time
        plan_status_list['end_time'] = pcp_obj.work_schedule_plan.end_time
        plan_status_list['product_no'] = pcp_obj.product_day_plan.product_batching.stage_product_batch_no
        plan_status_list['plan_classes_uid'] = pcp_obj.plan_classes_uid
        plan_status_list['plan_trains'] = pcp_obj.plan_trains
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by(
            'created_date').last()
        if tfb_obj:
            plan_status_list['actual_trains'] = tfb_obj.actual_trains
        else:
            plan_status_list['actual_trains'] = None
        plan_status_list['status'] = ps_obj.status
        return Response({'results': plan_status_list}, status=200)


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


# @method_decorator([api_recorder], name="dispatch")
class StopPlan(APIView):
    """计划停止"""

    def sent_to_yikong(self):
        # 发送数据给易控
        test_dict = OrderedDict()
        test_dict['stopstate'] = '停止'
        try:
            WebService.issue(test_dict, 'stop')
        except Exception as e:
            raise ValidationError(e)
    @atomic()
    def get(self, request):
        params = request.query_params
        plan_id = params.get("id")
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        equip_name = params.get("equip_name")
        pcp_obj = ProductClassesPlan.objects.filter(id=plan_id).first()
        if pcp_obj.product_day_plan.product_batching.used_type != 4:  # 4对应配方的启用状态
            raise ValidationError("该计划对应配方未启用,无法下达")
        if not pcp_obj:
            return Response({'_': "胶料班次日计划没有数据"}, status=400)
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by('created_date').last()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        if ps_obj.status != '运行中':
            return Response({'_': "只有运行中的计划才能停止！"}, status=400)
        ps_obj.status = '停止'
        ps_obj.save()

        # temp_data = {
        #     'id': params.get("id", None),  # id
        #     'state': '完成',  # 计划状态：等待，运行中，完成
        #     'remark': 'u',
        #     'recstatus': '完成'
        # }
        equip_no = pcp_obj.product_day_plan.equip.equip_no
        if "0" in equip_no:
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        # temp = IssueWorkStation('IfdownShengchanjihua' + ext_str, temp_data)
        # temp.update_to_db()

        from work_station import models as md
        model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownRecipePloy', 'IfdownRecipeOil1',
                      'IfdownRecipeCb', 'IfdownPmtRecipe']
        for model_str in model_list:
            model_name = getattr(md, model_str + ext_str)
            model_name.objects.all().update(recstatus='待停止')
        # self.sent_to_yikong()  # 发送数据给易控
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
        product_process_details = product_batching.process_details.filter(delete_flag=False)
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
                "type": "C",  # 炭黑
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
                "type": "O",  # 油料为O
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipePloy(self, product_batching, product_batching_details):
        datas = []
        gum_list = GlobalCode.objects.filter(global_type__type_name="胶料").values_list("global_name", flat=True)
        product_batching_details = product_batching_details.filter(material__material_type__global_name__in=gum_list)
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": pbd.actual_weight,
                "error_allow": pbd.standard_error,
                "recipe_name": product_batching.stage_product_batch_no,
                "act_code": 1 if pbd.auto_flag else 0,  # ?
                "type": "",  # 胶料 P
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipeMix(self, product_batching, product_process_details):
        datas = []
        for ppd in product_process_details:
            data = {
                "id": ppd.id,
                "set_condition": ppd.condition.condition if ppd and ppd.condition else None,  # ? 条件名称还是条件代码
                "set_time": int(ppd.time) if ppd.time else 0,
                "set_temp": int(ppd.temperature) if ppd.temperature else 0,
                "set_ener": ppd.energy,
                "set_power": ppd.power,
                "act_code": ppd.action.code,
                "set_pres": int(ppd.pressure) if ppd.pressure else 0,
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
            'setno': params.get("plan_trains", 1),  # 设定车次
            'actno': params.get("actual_trains", 0),  # 当前车次
            'oper': self.request.user.username,  # 操作员角色
            'state': '运行中',  # 计划状态：等待，运行中，完成
            'remark': '1',  # 计划单条下发默认值为1      c 创建,  u 更新 ,  d 删除 / 在炭黑表里表示增删改  计划表里用于标注批量计划的顺序
            'recstatus': '等待',  # 等待， 运行中， 完成
        }
        return data

    # 2020-09-04  万龙王工要求讲 炭黑油料胶料三张表合并  顾做次改动

    def _map_RecipeWeigh(self, product_batching, product_batching_details):
        # 胶料，油料，炭黑的合表
        datas = self._map_RecipePloy(product_batching, product_batching_details) + self._map_RecipeOil1(
            product_batching, product_batching_details) + self._map_RecipeCb(product_batching, product_batching_details)

        return datas

    def _sync(self, args, params=None, ext_str=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe).issue_to_db()

        RecipeWeigh = self._map_RecipeWeigh(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeWeigh' + ext_str, RecipeWeigh).batch_to_db()
        # RecipeCb = self._map_RecipeCb(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipeCb' + ext_str, RecipeCb).batch_to_db()
        # RecipeOil1 = self._map_RecipeOil1(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipeOil1' + ext_str, RecipeOil1).batch_to_db()
        # RecipePloy = self._map_RecipePloy(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipePloy' + ext_str, RecipePloy).batch_to_db()
        RecipeMix = self._map_RecipeMix(product_batching, product_process_details)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix).batch_to_db()
        Shengchanjihua = self._map_Shengchanjihua(params, pcp_obj)
        IssueWorkStation('IfdownShengchanjihua' + ext_str, Shengchanjihua).issue_to_db()

    def _sync_update(self, args, params=None, ext_str=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe).update_to_db()

        RecipeWeigh = self._map_RecipeWeigh(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeWeigh' + ext_str, RecipeWeigh).batch_update_to_db()
        # RecipeCb = self._map_RecipeCb(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipeCb' + ext_str, RecipeCb).batch_update_to_db()
        # RecipeOil1 = self._map_RecipeOil1(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipeOil1' + ext_str, RecipeOil1).batch_update_to_db()
        # RecipePloy = self._map_RecipePloy(product_batching, product_batching_details)
        # IssueWorkStation('IfdownRecipePloy' + ext_str, RecipePloy).batch_update_to_db()
        RecipeMix = self._map_RecipeMix(product_batching, product_process_details)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix).batch_update_to_db()
        # 重传逻辑只修改计划状态
        Shengchanjihua = {
            'id': params.get("id"),  # id
            'recstatus': '配方需重传',  # 等待， 运行中， 完成
        }
        IssueWorkStation('IfdownShengchanjihua' + ext_str, Shengchanjihua).update_to_db()

    def sent_to_yikong(self, params, pcp_obj):
        # 计划下达到易控组态
        test_dict = OrderedDict()  # 传给易控组态的数据
        test_dict['recipe_name'] = params.get("stage_product_batch_no", None)
        test_dict['recipe_code'] = params.get("stage_product_batch_no", None)
        test_dict['latesttime'] = params.get("day_time", None)
        test_dict['planid'] = params.get("plan_classes_uid", None)
        test_dict['starttime'] = params.get("begin_time", None)
        test_dict['stoptime'] = params.get("end_time", None)
        test_dict['grouptime'] = params.get("classes", None)
        test_dict['groupoper'] = params.get("group", None)
        test_dict['setno'] = params.get("plan_trains", None)
        test_dict['oper'] = params.get("operation_user", None)
        test_dict['runstate'] = '运行中'
        test_dict['machineno'] = strtoint(params.get("equip_name", None))  # 易控组态那边的机台euqip_no是int类型
        test_dict['finishno'] = params.get("actual_trains", None)
        test_dict['weight'] = pcp_obj.product_day_plan.product_batching.batching_weight
        test_dict['sp_number'] = pcp_obj.product_day_plan.product_batching.processes.sp_num
        try:
            WebService.issue(test_dict, 'plan')
        except Exception as e:
            raise ValidationError(e)

    @atomic()
    def post(self, request):

        params = request.data
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)

        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()

        if pcp_obj.product_day_plan.product_batching.used_type != 4:  # 4对应配方的启用状态
            raise ValidationError("该计划对应配方未启用,无法下达")

        # 校验计划与配方完整性

        uid_list = pcp_obj.product_day_plan.pdp_product_classes_plan.all().values_list("plan_classes_uid", flat=True)
        id_list = PlanStatus.objects.annotate(m_id=Max(id)).filter(plan_classes_uid__in=uid_list).values_list("id",
                                                                                                              flat=True)
        status_list = PlanStatus.objects.filter(id__in=id_list)
        if "运行中" in status_list:
            raise ValidationError("该机台当前已有运行中计划,无法下达新计划")
        elif "已下达" in status_list:
            raise ValidationError("该机台当前已有已下达计划,无法下达新计划")
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by('created_date').last()
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
        ps_obj.status = '已下达'
        ps_obj.save()

        # self.sent_to_yikong(params, pcp_obj)
        return Response({'_': '下达成功'}, status=200)

    @atomic()
    def put(self, request):
        params = request.data
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()
        if pcp_obj.product_day_plan.product_batching.used_type != 4:  # 4对应配方的启用状态
            raise ValidationError("该计划对应配方未启用,无法重传")
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by('created_date').last()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        equip_no = ps_obj.equip_no
        if "0" in equip_no:
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        if ps_obj.status != '运行中':
            return Response({'_': "只有运行中的计划才能重传！"}, status=400)
        self._sync_update(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str)
        # 模型类的名称需根据设备编号来拼接
        # 重传默认不修改plan_status
        # ps_obj.status = '运行'
        # ps_obj.save()
        return Response({'_': '重传成功'}, status=200)


'''
前端现有的重传计划接口调用的是下达计划的put方法，这个重传计划的接口基本没用了，先注释掉
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
'''


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
