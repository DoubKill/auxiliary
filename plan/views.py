import datetime
import json
from collections import OrderedDict

import requests
from django.db.models import Max
from django.db.transaction import atomic
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from basics.models import GlobalCode
from basics.views import CommonDeleteMixin
from mes.common_code import WebService, DecimalEncoder
from mes.conf import VERSION_EQUIP, hf_db
from mes.derorators import api_recorder
from plan.filters import ProductDayPlanFilter, PalletFeedbacksFilter
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, SchedulingResult
from plan.serializers import UpRegulationSerializer, DownRegulationSerializer, UpdateTrainsSerializer, \
    PalletFeedbacksPlanSerializer, PlanReceiveSerializer, ProductDayPlanSerializer
from production.models import PlanStatus, TrainsFeedbacks, MaterialTankStatus
from production.utils import strtoint
# Create your views here.
from recipe.models import ProductProcess, ProductBatching
from work_station.api import IssueWorkStation
from work_station.models import I_RECIPES_V, ProdOrdersImp, LogTable


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
    queryset = ProductClassesPlan.objects.filter(delete_flag=False).order_by('-id', 'sn')
    serializer_class = PalletFeedbacksPlanSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filter_class = PalletFeedbacksFilter

    # @atomic()
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


@method_decorator([api_recorder], name="dispatch")
class PlanStatusList(APIView):
    """计划管理当前机台计划展示"""

    def get(self, request):
        params = request.query_params
        equip_no = params.get('equip_no')
        ps_obj = PlanStatus.objects.filter(equip_no=equip_no, status='运行中').last()
        plan_status_list = {}
        if not ps_obj:
            return Response({'results': plan_status_list}, 200)
        if not ps_obj.status == '运行中':
            return Response({'results': plan_status_list}, 200)
        else:
            pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=ps_obj.plan_classes_uid).first()
            if not pcp_obj:
                return Response({'results': plan_status_list}, 200)
            plan_status_list['equip_no'] = equip_no
            plan_status_list['begin_time'] = pcp_obj.work_schedule_plan.start_time.strftime("%Y-%m-%d %H:%M:%S")
            plan_status_list['end_time'] = pcp_obj.work_schedule_plan.end_time.strftime("%Y-%m-%d %H:%M:%S")
            plan_status_list['product_no'] = pcp_obj.product_batching.stage_product_batch_no
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


@method_decorator([api_recorder], name="dispatch")
class StopPlan(APIView):
    """计划停止"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @atomic()
    def get(self, request):
        version = request.version
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

        equip_no = pcp_obj.product_day_plan.equip.equip_no
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]

        if version == "v1":
            from work_station import models as md
            model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownPmtRecipe', "IfdownRecipeWeigh"]
            for model_str in model_list:
                model_name = getattr(md, model_str + ext_str)
                model_name.objects.all().update(recstatus='待停止')
            ps_obj.status = '停止'
            ps_obj.save()
            pcp_obj.status = '停止'
            pcp_obj.save()
        elif version == "v2":
            data = OrderedDict()
            data['stopstate'] = '停止'
            data['planid'] = pcp_obj.plan_classes_uid
            data['no'] = ext_str
            try:
                WebService.issue(data, 'stop', equip_no=ext_str, equip_name="上辅机")
            except requests.exceptions.ConnectTimeout:
                raise ValidationError(f"上辅机网络连接超时")
            except Exception as e:
                raise
            ps_obj.status = '停止'
            ps_obj.save()
            pcp_obj.status = '停止'
            pcp_obj.save()

        else:
            from work_station import models as md
            model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownPmtRecipe', "IfdownRecipeWeigh"]
            for model_str in model_list:
                model_name = getattr(md, model_str + ext_str)
                model_name.objects.all().update(recstatus='待停止')
            ps_obj.status = '停止'
            ps_obj.save()
            pcp_obj.status = '停止'
            pcp_obj.save()
        return Response({'_': '修改成功'}, status=200)


@method_decorator([api_recorder], name="dispatch")
class IssuedPlan(APIView):
    """下达计划"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def plan_recipe_integrity_check(self, pcp_obj):
        # 检验计计划配方是否可用
        if not pcp_obj:
            raise ValidationError("无对应班次计划")
        try:
            product_batching = pcp_obj.product_day_plan.product_batching
        except:
            raise ValidationError("无对应日计划胶料配料标准")
        if product_batching.used_type != 4:
            raise ValidationError("该计划所选配方未启用")
        # # 不允许创建上一个班次的计划，(ps:举例说明 比如现在是中班，那么今天的早班是创建不了的，今天之前的计划也是创建不了的)
        end_time = pcp_obj.work_schedule_plan.end_time  # 取班次的结束时间
        now_time = datetime.datetime.now()
        if now_time > end_time:
            raise ValidationError(
                f'{end_time.strftime("%Y-%m-%d")}的{pcp_obj.work_schedule_plan.classes.global_name}的计划不允许现在下达')
        # 胶料配料详情，一份胶料对应多个配料
        product_batching_details = product_batching.batching_details.filter(delete_flag=False)
        if not product_batching_details:
            raise ValidationError("胶料配料详情为空，该计划不可用")
        product_process = ProductProcess.objects.filter(product_batching=product_batching).first()
        # if not product_process:
        #     raise ValidationError("胶料配料步序为空，该计划不可用")
        # 步序详情，一份通用步序对应多份步序详情
        product_process_details = product_batching.process_details.filter(delete_flag=False)
        # if not product_process_details:
        #     raise ValidationError("胶料配料步序详情为空，该计划不可用")

        return product_batching, product_batching_details, product_process, product_process_details, pcp_obj

    def _map_PmtRecipe(self, pcp_object, product_process, product_batching, equip_no):
        if product_batching.used_type != 4:
            raise ValidationError("该计划所选配方未启用")
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no__icontains=equip_no,
                                                                                          batching_type=1,
                                                                                          used_type=4).first()
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方或者未启用，请关联后重试")
            actual_product_process = actual_product_batching.processes
            if not actual_product_process:
                raise ValidationError("胶料配料步序为空，该计划不可用")
        else:
            actual_product_process = product_process
            actual_product_batching = product_batching
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            if not actual_product_process:
                raise ValidationError("胶料配料步序为空，该计划不可用")
        data = {
            "id": actual_product_process.id,
            "lasttime": str(pcp_object.product_day_plan.plan_schedule.day_time),
            "oper": self.request.user.username,
            "recipe_code": actual_product_batching.stage_product_batch_no,
            "recipe_name": actual_product_batching.stage_product_batch_no,
            "equip_code": actual_product_process.equip_code if actual_product_process.equip_code else 0.0,  # 锁定解锁
            "reuse_time": actual_product_process.reuse_time,
            "mini_time": actual_product_process.mini_time,
            "max_time": actual_product_process.over_time,
            "mini_temp": actual_product_process.mini_temp,
            "max_temp": actual_product_process.max_temp,
            "over_temp": actual_product_process.over_temp,
            "if_not": 0 if actual_product_process.reuse_flag else -1,  # 是否回收  国自(true:回收， false:不回收)  万龙（0:回收， -1:不回收）
            "temp_zz": actual_product_process.zz_temp,
            "temp_xlm": actual_product_process.xlm_temp,
            "temp_cb": actual_product_process.cb_temp,
            # "tempuse": 0 if actual_product_process.temp_use_flag else 1,
            # 三区水温是否启用 国自(true:启用， false:停用)  万龙(0:三区水温启用， 1:三区水温停用)
            "tempuse": 1 if actual_product_process.temp_use_flag else 0,
            # 三区水温是否启用 国自(true:启用， false:停用)  元嘉(1:三区水温启用， 0:三区水温停用)
            "usenot": 0 if actual_product_batching.used_type == 4 else 1,  # 配方是否启用 国自(4:启用， 其他数字:不可用)  万龙(0:启用， 1:停用)
            "recstatus": "等待",
        }
        return data

    def _map_RecipeCb(self, product_batching, product_batching_details):
        datas = []
        product_batching_details = product_batching_details.filter(type=2)
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": round(pbd.actual_weight,2),
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
        product_batching_details = product_batching_details.filter(type=3)
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": round(pbd.actual_weight,2),
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
        product_batching_details = product_batching_details.filter(type=1)
        for pbd in product_batching_details:
            data = {
                "id": pbd.id,
                "mname": pbd.material.material_name,
                "set_weight": round(pbd.actual_weight,2),
                "error_allow": pbd.standard_error,
                "recipe_name": product_batching.stage_product_batch_no,
                "act_code": 1 if pbd.auto_flag else 0,  # ?
                "type": "P",  # 胶料 P
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipeMix(self, product_batching, product_process_details, equip_no):
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no__icontains=equip_no,
                                                                                          batching_type=1).first()
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            actual_product_process_details = actual_product_batching.process_details.filter(delete_flag=False)
            if not actual_product_process_details:
                raise ValidationError("胶料配料步序详情为空，该计划不可用")
        else:
            actual_product_process_details = product_process_details
            actual_product_batching = product_batching
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            if not actual_product_process_details:
                raise ValidationError("胶料配料步序详情为空，该计划不可用")
        datas = []
        for ppd in actual_product_process_details:
            data = {
                "id": ppd.id,
                "set_condition": ppd.condition.condition if ppd and ppd.condition else None,  # ? 条件名称还是条件代码
                "set_time": int(ppd.time) if ppd.time else 0,
                "set_temp": int(ppd.temperature) if ppd.temperature else 0,
                "set_ener": ppd.energy,
                "set_power": ppd.power,
                "act_code": ppd.action.action,
                "set_pres": ppd.pressure if ppd.pressure else 0.0,
                "set_rota": int(ppd.rpm) if ppd.rpm else 0,
                "recipe_name": actual_product_batching.stage_product_batch_no,
                "recstatus": "等待",
                "sn": ppd.sn
            }
            datas.append(data)
        id_list = [x.get("id") for x in datas]
        id_list.sort()
        datas.sort(key=lambda x: x.get("sn"))
        for x in datas:
            index = datas.index(x)
            x["id"] = id_list[index]
            x.pop("sn")
        return datas

    def _map_Shengchanjihua(self, params, pcp_obj):
        data = {
            'id': pcp_obj.id,  # id
            'recipe': params.get("stage_product_batch_no", None),  # 配方名
            'recipeid': params.get("stage_product_batch_no", None),  # 配方编号
            'lasttime': params.get("day_time"),  # 班日期
            'planid': params.get("plan_classes_uid", None),  # 计划编号  plan_no
            'startime': pcp_obj.work_schedule_plan.start_time.strftime("%Y-%m-%d %H:%M:%S"), # 开始时间
            'stoptime': pcp_obj.work_schedule_plan.end_time.strftime("%Y-%m-%d %H:%M:%S"),  # 结束时间
            'grouptime': params.get("classes", None),  # 班次
            'groupoper': params.get("group", None),  # 班组????
            'setno': params.get("plan_trains", 1),  # 设定车次
            'actno': 0,  # 当前车次
            'oper': self.request.user.username,  # 操作员角色
            'state': '等待',  # 计划状态：等待，运行中，完成
            'remark': '0',  # 计划单条下发默认值为1      c 创建,  u 更新 ,  d 删除 / 在炭黑表里表示增删改  计划表里用于标注批量计划的顺序
            'recstatus': '等待',  # 等待， 运行中， 完成
        }
        return data

    # 2020-09-04  万龙王工要求讲 炭黑油料胶料三张表合并  顾做次改动

    def _map_RecipeWeigh(self, product_batching, product_batching_details):
        # 胶料，油料，炭黑的合表
        datas = self._map_RecipePloy(product_batching, product_batching_details) + self._map_RecipeOil1(
            product_batching, product_batching_details) + self._map_RecipeCb(product_batching, product_batching_details)
        if not datas:
            raise ValidationError("胶料配料详情为空，该计划不可用")
        return datas

    def _sync(self, args, params=None, ext_str="", equip_no=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching, equip_no)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe, ext_str).issue_to_db()

        RecipeWeigh = self._map_RecipeWeigh(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeWeigh' + ext_str, RecipeWeigh, ext_str).batch_to_db()

        RecipeMix = self._map_RecipeMix(product_batching, product_process_details, equip_no)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix, ext_str).batch_to_db()

        Shengchanjihua = self._map_Shengchanjihua(params, pcp_obj)
        IssueWorkStation('IfdownShengchanjihua' + ext_str, Shengchanjihua, ext_str).issue_to_db()

    def _sync_update(self, args, params=None, ext_str="", equip_no=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        PmtRecipe = self._map_PmtRecipe(pcp_obj, product_process, product_batching, equip_no)
        IssueWorkStation('IfdownPmtRecipe' + ext_str, PmtRecipe, ext_str).update_to_db()

        RecipeWeigh = self._map_RecipeWeigh(product_batching, product_batching_details)
        IssueWorkStation('IfdownRecipeWeigh' + ext_str, RecipeWeigh, ext_str).batch_update_to_db()

        RecipeMix = self._map_RecipeMix(product_batching, product_process_details, equip_no)
        IssueWorkStation('IfdownRecipeMix' + ext_str, RecipeMix, ext_str).batch_update_to_db()

        Shengchanjihua = self._map_Shengchanjihua(params, pcp_obj)
        Shengchanjihua.update(recstatus='配方需重传')
        IssueWorkStation('IfdownShengchanjihua' + ext_str, Shengchanjihua, ext_str).update_to_db()

    def _map_recipe(self, pcp_object, product_process, product_batching, equip_no):
        # 映射全小写代表对接国自上辅机
        if product_batching.used_type != 4:
            raise ValidationError("该计划所选配方未启用")
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no__icontains=equip_no,
                                                                                          batching_type=1).first()
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            actual_product_process = actual_product_batching.processes
            if not actual_product_process:
                raise ValidationError("胶料配料步序为空，该计划不可用")
        else:
            actual_product_process = product_process
            actual_product_batching = product_batching
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            if not actual_product_process:
                raise ValidationError("胶料配料步序为空，该计划不可用")
        data = OrderedDict()
        data["id"] = actual_product_process.id
        data["latesttime"] = str(pcp_object.product_day_plan.plan_schedule.day_time)
        data["oper"] = self.request.user.username
        data["recipe_name"] = actual_product_batching.stage_product_batch_no
        data["recipe_code"] = actual_product_batching.stage_product_batch_no
        data["equip_code"] = actual_product_process.equip_code  # 锁定解锁
        data["mini_time"] = actual_product_process.mini_time
        data["max_time"] = actual_product_process.over_time  # 炼胶超时时间
        data["mini_temp"] = actual_product_process.mini_temp
        data["max_temp"] = actual_product_process.max_temp
        data["over_temp"] = actual_product_process.over_temp
        data["reuse_time"] = actual_product_process.reuse_time
        data["if_not"] = 1 if actual_product_process.reuse_flag else 0  # 是否回收  国自(true:回收， false:不回收)  gz上辅机（1:回收， 0:不回收）
        data["rot_temp"] = actual_product_process.zz_temp
        data["shut_temp"] = actual_product_process.xlm_temp
        data["side_temp"] = actual_product_process.cb_temp
        data["temp_on_off"] = 0 if actual_product_process.temp_use_flag else 1
        data["sp_num"] = actual_product_process.sp_num
        # if int(equip_no) in [1, 7, 8, 9]:
        #     data["sp_num"] = actual_product_process.sp_num
        if int(equip_no) in [12, 13, 14, 15]:
            if data.get("max_temp") <= 0:
                raise ValidationError(f"Z{equip_no}# 元嘉上辅机进胶最高温度不能小于等于0")
        # 三区水温是否启用 国自(true:启用， false:停用)  万龙(0:三区水温启用， 1:三区水温停用)
        data["recipe_off"] = 0 if actual_product_batching.used_type == 4 else 1  # 配方是否启用 国自(4:启用， 其他数字:不可用)  万龙(0:启用， 1:停用)
        data["machineno"] = int(equip_no)
        if int(equip_no) in [12, 13]:
            data['ring_time'] = actual_product_process.ch_time
            data['smash_time'] = actual_product_process.dj_time
            data['snap_time'] = actual_product_process.ld_time
            data['usingif'] = int(actual_product_process.use_flag)
        return data

    def _map_cb(self, product_batching, product_batching_details, equip_no):
        datas = []
        product_batching_details = product_batching_details.filter(type=2)
        # equip = product_batching.equip.equip_no
        if len(equip_no) == 1:
            equip = "Z0" + equip_no
        else:
            equip = "Z" + equip_no
        for pbd in product_batching_details:
            material_name = pbd.material.material_name
            tank_no = pbd.tank_no
            if tank_no is None:
                if material_name == "卸料":
                    tank_no = "卸料"
                else:
                    tank_no = ""
            if material_name == "卸料":
                if not MaterialTankStatus.objects.filter(material_name=material_name, tank_type='1',
                                                         equip_no=equip).exists():
                    raise ValidationError("炭黑罐中未匹配到该物料，请检查")
            else:
                if not MaterialTankStatus.objects.filter(tank_no=tank_no, material_name=material_name, tank_type='1',
                                                         equip_no=equip).exists():
                    raise ValidationError("炭黑罐中未匹配到该物料，请检查")
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = "卸料" if tank_no == "卸料" else "炭黑罐" + tank_no
            data["matcode"] = pbd.material.material_name
            data["set_weight"] = round(pbd.actual_weight,2)
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = pbd.sn
            data["mattype"] = "C"  # 炭黑
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_oil(self, product_batching, product_batching_details, equip_no):
        datas = []
        product_batching_details = product_batching_details.filter(type=3)
        if len(equip_no) == 1:
            equip = "Z0" + equip_no
        else:
            equip = "Z" + equip_no
        for pbd in product_batching_details:
            material_name = pbd.material.material_name
            tank_no = pbd.tank_no
            if tank_no is None:
                if material_name == "卸料":
                    tank_no = "卸料"
                else:
                    tank_no = ""
            if material_name == "卸料":
                if not MaterialTankStatus.objects.filter(material_name=material_name, tank_type='2',
                                                         equip_no=equip).exists():
                    raise ValidationError("油料罐中未匹配到该物料，请检查")
            else:
                if not MaterialTankStatus.objects.filter(tank_no=tank_no, material_name=material_name, tank_type='2',
                                                         equip_no=equip).exists():
                    raise ValidationError("油料罐中未匹配到该物料，请检查")
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = "卸料" if tank_no == "卸料" else "油料罐" + tank_no
            data["matcode"] = pbd.material.material_name
            data["set_weight"] = round(pbd.actual_weight,2)
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = pbd.sn
            data["mattype"] = "O"  # 油料
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_ploy(self, product_batching, product_batching_details, equip_no):
        datas = []
        product_batching_details = product_batching_details.filter(type=1)
        for pbd in product_batching_details:
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = pbd.material.material_name
            data["set_weight"] = round(pbd.actual_weight,2)
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = pbd.sn
            data["mattype"] = "P"  # 炭黑
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_weigh(self, product_batching, product_batching_details, equip_no):
        # 胶料，油料，炭黑的合表
        ploy_data = self._map_ploy(product_batching, product_batching_details, equip_no)
        oil_data = self._map_oil(product_batching, product_batching_details, equip_no)
        cb_data = self._map_cb(product_batching, product_batching_details, equip_no)
        if not oil_data:
            oil_data = [{'id': product_batching.id, 'matname': '', 'set_weight': 0, 'error_allow': 0,
                         'recipe_name': product_batching.stage_product_batch_no, 'act_code': 0,
                         'mattype': 'O', 'machineno': int(equip_no), 'matcode': ''}]
        if not cb_data:
            cb_data = [{'id': product_batching.id, 'matname': '', 'set_weight': 0, 'error_allow': 0,
                         'recipe_name': product_batching.stage_product_batch_no, 'act_code': 0,
                        'mattype': 'C', 'machineno': int(equip_no), 'matcode': ''}]
        datas = ploy_data + oil_data + cb_data
        if not datas:
            raise ValidationError("胶料配料详情为空，该计划不可用")
        return datas

    def _map_mix(self, product_batching, product_process_details, equip_no):
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no__icontains=equip_no,
                                                                                          batching_type=1).first()
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            actual_product_process_details = actual_product_batching.process_details.filter(delete_flag=False)
            if not actual_product_process_details:
                raise ValidationError("胶料配料步序详情为空，该计划不可用")
        else:
            actual_product_process_details = product_process_details
            actual_product_batching = product_batching
            if not actual_product_batching:
                raise ValidationError("当前计划未关联机台配方，请关联后重试")
            if not actual_product_process_details:
                raise ValidationError("胶料配料步序详情为空，该计划不可用")
        datas = []
        for ppd in actual_product_process_details:
            data = OrderedDict()
            data["id"] = ppd.id
            data["recipe_name"] = actual_product_batching.stage_product_batch_no
            data["set_condition"] = ppd.condition.condition if ppd and ppd.condition else None  # ? 条件名称还是条件代码
            data["set_time"] = int(ppd.time) if ppd.time else 0
            data["set_temp"] = int(ppd.temperature) if ppd.temperature else 0
            data["set_ener"] = ppd.energy
            data["set_power"] = ppd.power
            data["act_code"] = ppd.action.action
            data["set_pres"] = ppd.pressure if ppd.pressure else 0.0
            data["set_rota"] = int(ppd.rpm) if ppd.rpm else 0
            data["ID_step"] = ppd.sn
            data["machineno"] = int(equip_no)
            datas.append(data)
        id_list = [x.get("id") for x in datas]
        id_list.sort()
        datas.sort(key=lambda x: x.get("ID_step"))
        for x in datas:
            index = datas.index(x)
            x["id"] = id_list[index]
        # 12，13，14，15元嘉上辅机配方步序特殊需判断是否以配方结束结尾
        if int(equip_no) in [12,13,14,15]:
            if datas[-1].get("set_condition") != "配方结束":
                raise ValidationError(f"Z{equip_no}#元嘉上辅机配方步序必须以配方结束结尾")
        return datas

    def _map_plan(self, params, pcp_obj, equip_no):
        data = OrderedDict()
        start_time = pcp_obj.work_schedule_plan.start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time = pcp_obj.work_schedule_plan.end_time.strftime("%Y-%m-%d %H:%M:%S")
        product_no = pcp_obj.product_batching.stage_product_batch_no
        data['id'] = pcp_obj.id  # id
        data['recipe_name'] = product_no  # 配方名
        data['recipe_code'] = product_no  # 配方编号
        data['latesttime'] = pcp_obj.created_date.strftime("%Y-%m-%d %H:%M:%S")  # 计划创建时间
        data['planid'] = pcp_obj.plan_classes_uid  # 计划编号  plan_no
        data['starttime'] = start_time  # 开始时间
        data['stoptime'] = end_time  # 结束时间
        data['grouptime'] = pcp_obj.work_schedule_plan.classes.global_name  # 班次
        data['groupoper'] = pcp_obj.work_schedule_plan.group.global_name  # 班组????
        data['setno'] = pcp_obj.plan_trains
        data['actno'] = 0  # 当前车次
        data['oper'] = self.request.user.username  # 操作员角色
        data['runstate'] = '运行中'  # 计划状态：等待，运行中，完成
        data['runmark'] = '0'  # 计划单条下发默认值为1   计划表里用于标注批量计划的顺序, 按时弃用为0
        data["machineno"] = int(equip_no)
        return data

    def _sync_interface(self, args, params=None, ext_str="", equip_no=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        recipe = self._map_recipe(pcp_obj, product_process, product_batching, ext_str)
        try:
            status, text = WebService.issue(recipe, 'recipe_con', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("计划下达失败，计划重复|配方不存在|计划下达错误")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")

        if not status:
            raise ValidationError(f"主配方下达失败:{text}")
        weigh = self._map_weigh(product_batching, product_batching_details, ext_str)
        weigh_data = {"json": json.dumps({"datas": weigh}, cls=DecimalEncoder)}  # 这是易控那边为获取批量数据约定的数据格式
        try:
            status, text = WebService.issue(weigh_data, 'recipe_weight', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方称量已存在于上辅机，请勿重复下达")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")
        if not status:
            raise ValidationError(f"配方称量下达失败:{text}")
        mix = self._map_mix(product_batching, product_process_details, ext_str)
        mix_data = {"json": json.dumps({"datas": mix}, cls=DecimalEncoder)}
        try:
            status, text = WebService.issue(mix_data, 'recipe_step', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方步序已存在于上辅机，请勿重复下达")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")
        if not status:
            raise ValidationError(f"配方步序下达失败:{text}")
        plan = self._map_plan(params, pcp_obj, ext_str)
        try:
            status, text = WebService.issue(plan, 'plan', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("计划下达失败，计划重复|配方不存在|计划下达错误")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")
        if not status:
            raise ValidationError(f"计划下达失败:{text}")

    def _sync_update_interface(self, args, params=None, ext_str="", equip_no=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        recipe = self._map_recipe(pcp_obj, product_process, product_batching, ext_str)
        try:
            status, text = WebService.issue(recipe, 'recipe_con_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方不存在于上辅机，请检查上辅机")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")

        if not status:
            raise ValidationError(f"主配方重传失败:{text}")
        weigh = self._map_weigh(product_batching, product_batching_details, ext_str)
        weigh_data = {"json": json.dumps({"datas": weigh}, cls=DecimalEncoder)}  # 这是易控那边为获取批量数据约定的数据格式
        try:
            status, text = WebService.issue(weigh_data, 'recipe_weight_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方称量不存在于上辅机，请检查上辅机")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")
        if not status:
            raise ValidationError(f"配方称量重传失败:{text}")
        mix = self._map_mix(product_batching, product_process_details, ext_str)
        mix_data = {"json": json.dumps({"datas": mix}, cls=DecimalEncoder)}
        try:
            status, text = WebService.issue(mix_data, 'recipe_step_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方步序不存在于上辅机，请检查上辅机")
        except Exception as e:
            raise ValidationError(f"{equip_no} 网络连接异常: {e}")
        if not status:
            raise ValidationError(f"配方步序重传失败:{text}")

    # @atomic()
    def post(self, request):
        version = request.version
        params = request.data
        plan_id = params.get("id", None)
        if plan_id is None:
            return Response({'_': "没有传id"}, status=400)
        equip_no = params.get("equip_name", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
        pcp_obj = ProductClassesPlan.objects.filter(id=int(plan_id)).first()

        if pcp_obj.product_day_plan.product_batching.used_type != 4:  # 4对应配方的启用状态
            raise ValidationError("该计划对应配方未启用,无法下达")

        # 校验计划与配方完整性
        ps_obj = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by('created_date').last()
        if not ps_obj:
            return Response({'_': "计划状态变更没有数据"}, status=400)
        equip_no = ps_obj.equip_no
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        if ps_obj.status != '等待':
            return Response({'_': "只有等待中的计划才能下达！"}, status=400)
        if version == "v1":
            self._sync(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str, equip_no=equip_no)
            ps_obj.status = '已下达'
            ps_obj.save()
            pcp_obj.status = '已下达'
            pcp_obj.save()
            # self.send_to_yikong(params, pcp_obj)
        elif version == "v2":
            self._sync_interface(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                                 equip_no=equip_no)
            # 模型类的名称需根据设备编号来拼接
            ps_obj.status = '运行中'
            ps_obj.save()
            pcp_obj.status = '运行中'
            pcp_obj.save()
        elif version == "v3":
            # 四号机只会有计划订单下达，所以单独写一块代码， 至于封装问题，等逻辑处理完再说
            recipe_name = pcp_obj.product_batching.stage_product_batch_no
            hf_recipe_version = pcp_obj.product_batching.precept
            if hf_recipe_version is None:
                hf_recipe_version = 1
            else:
                try:
                    hf_recipe_version = int(pcp_obj.product_batching.precept)
                except Exception as e:
                    raise ValidationError("ZO4机台配方的版本/方案异常，请检查是否为标准数字")
            host_id = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))/111
            if ProdOrdersImp.objects.using(hf_db).all().order_by("pori_id").last().pori_pror_status in [1, 2]:
                raise ValidationError("当前机台有计划正在执行，禁止下达新计划")
            try:
                I_RECIPES_V.objects.using("H-Z04").filter(recipe_blocked='no')
                ProdOrdersImp.objects.using(hf_db).filter(pori_line_name='Z04',
                                                            pori_recipe_code=recipe_name,
                                                            pori_recipe_version=hf_recipe_version).delete()
                ProdOrdersImp.objects.using(hf_db).create(
                    pori_line_name='Z04',
                    pori_order_number=pcp_obj.plan_classes_uid,
                    pori_recipe_code=recipe_name,
                    pori_recipe_version=hf_recipe_version,
                    pori_batch_quantity_set=pcp_obj.plan_trains,
                    pori_order_weight=pcp_obj.weight,
                    pori_pror_blocked=0,
                    pori_function=9,
                    pori_host_id=host_id
                )
            except Exception as e:
                lt = LogTable.objects.using(hf_db).filter(lgtb_host_id=host_id).order_by("lgtb_id").last()
                if not lt:
                    raise ValidationError(f"未知错误：{e}")
                raise ValidationError(f"{lt.lgtb_sql_errormessage}||{lt.lgtb_pks_errormessage}")
            else:
                plan_status =  ProdOrdersImp.objects.using(hf_db).filter(pori_line_name='Z04',
                                                            pori_order_number=pcp_obj.plan_classes_uid,
                                                            pori_recipe_code=recipe_name,
                                                            pori_recipe_version=hf_recipe_version).order_by("pori_id").last().pori_status
                if plan_status < 0:
                    lt = LogTable.objects.using(hf_db).filter(lgtb_host_id=host_id).order_by("lgtb_id").last()
                    raise ValidationError(f"{lt.lgtb_sql_errormessage}||{lt.lgtb_pks_errormessage}")
                else:
                    ps_obj.status = "已下达"
                    ps_obj.save()
                    pcp_obj.status = '已下达'
                    pcp_obj.save()
                    return Response({'_': '下达成功'}, status=200)

        else:
            self._sync_interface(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                                 equip_no=equip_no)
            # 模型类的名称需根据设备编号来拼接
            ps_obj.status = '运行中'
            ps_obj.save()
            pcp_obj.status = '运行中'
            pcp_obj.save()
        return Response({'_': '下达成功'}, status=200)

    @atomic()
    def put(self, request):
        version = request.version
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
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        if ps_obj.status != '运行中':
            return Response({'_': "只有运行中的计划才能重传！"}, status=400)
        if version == "v1":
            self._sync_update(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                              equip_no=equip_no)
        elif version == "v2":
            self._sync_update_interface(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                                        equip_no=equip_no)
        elif version == "v3":
            raise ValidationError("特殊机台不支持重传")
        else:
            self._sync_update(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                              equip_no=equip_no)
        return Response({'_': '重传成功'}, status=200)


@method_decorator([api_recorder], name="dispatch")
class PlanReceive(CreateAPIView):
    """
        接受上辅机计划数据接口
        """
    # permission_classes = ()
    # authentication_classes = ()
    # permission_classes = (IsAuthenticated,)
    serializer_class = PlanReceiveSerializer
    queryset = ProductDayPlan.objects.all()

    @atomic()
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class HfRecipeList(APIView):

    def get(self, request):
        try:
            recipe_set = I_RECIPES_V.objects.using("H-Z04").filter(recipe_blocked='no').values("recipe_number", "recipe_code", "recipe_version", "recipe_blocked", "recipe_type")
            ret = list(recipe_set)
        except Exception as e:
            raise ValidationError(f"HF数据库连接异常,详情: {e}")
        else:
            return Response({"results": ret})


@method_decorator([api_recorder], name="dispatch")
class LabelPlanInfo(APIView):
    """根据计划编号，获取工厂日期和班组"""

    def get(self, request):
        plan_classes_uid = self.request.query_params.get('planid')
        plan = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid).first()
        if plan:
            return Response({'factory_date': plan.work_schedule_plan.plan_schedule.day_time,
                             'group': plan.work_schedule_plan.group.global_name})
        else:
            return Response({'factory_date': '',
                             'group': ''})


@method_decorator([api_recorder], name="dispatch")
class SchedulingResultView(APIView):

    def get(self, request):
        factory_date = self.request.query_params.get('factory_date')
        equip_no = self.request.query_params.get('equip_no')
        last_result = SchedulingResult.objects.using('mes').filter(factory_date=factory_date).order_by('id').last()
        if not last_result:
            return Response([])
        else:
            data = list(SchedulingResult.objects.using('mes').filter(
                schedule_no=last_result.schedule_no,
                equip_no=equip_no
            ).order_by('id').values('id', 'recipe_name', 'plan_trains', 'time_consume', 'desc', 'status'))
        return Response(data)

    def post(self, request):
        result_id = self.request.data.get('result_id')
        if not isinstance(result_id, list):
            raise ValidationError('bad request')
        SchedulingResult.objects.using('mes').filter(id__in=result_id).update(status='已下发')
        return Response('OK')


@method_decorator([api_recorder], name="dispatch")
class PlanIssueValidate(APIView):

    def get(self, request):
        plan_id = self.request.query_params.get('plan_id')
        try:
            plan = ProductClassesPlan.objects.get(id=plan_id)
        except Exception:
            raise ValidationError('该计划不存在！')
        pb = ProductBatching.objects.filter(batching_type=1,
                                            equip=plan.equip,
                                            stage_product_batch_no=plan.product_batching.stage_product_batch_no,
                                            used_type=4).first()
        if not pb:
            raise ValidationError('该计划配方未启用或不存在！')
        product_batching_details = pb.batching_details.filter(delete_flag=False)
        product_process_details = pb.process_details.filter(delete_flag=False)
        cb_cnt = product_batching_details.exclude(material__material_name='卸料').filter(type=2).count()  # 炭黑称量数量
        oil_cnt = product_batching_details.exclude(material__material_name='卸料').filter(type=3).count()  # 油料称量数量

        cb_xl_cnt = product_batching_details.filter(type=2, material__material_name='卸料').count()  # 炭黑卸料数量
        oil_xl_cnt = product_batching_details.filter(type=3, material__material_name='卸料').count()  # 油料卸料数量

        add_cb_cnt = product_process_details.filter(
            action__action__icontains='炭黑').count()  # 步序加炭黑次数
        add_oil_actions = product_process_details.filter(
            action__action__icontains='油').values_list('action__action', flat=True)
        add_oil_cnt = 0  # 步序加油料次数
        for oil_action in add_oil_actions:
            for i in oil_action:
                if i == '油':
                    add_oil_cnt += 1

        last_action_process = product_process_details.exclude(
            condition__condition__in=('配方结束', '同时执行')
        ).filter(condition__isnull=False).order_by('sn').last()
        open_door_process = product_process_details.filter(action__action='开卸料门').order_by('sn').last()
        if cb_xl_cnt != add_cb_cnt:
            return Response({'success': False, 'msg': '配方步序有误：配方炭黑称量卸料次数与步序里的加炭黑次数不一致！'})
        if oil_xl_cnt != add_oil_cnt:
            return Response({'success': False, 'msg': '配方步序有误，油料称量卸料次数与步序里的加油次数不一致！'})
        if cb_cnt and not add_cb_cnt:  # 有炭黑称量，无加炭黑步序
            return Response({'success': False, 'msg': '配方步序有误，炭黑称量列表中有炭黑！'})
        if not cb_cnt and add_cb_cnt:  # 无炭黑称量，有加炭黑步序
            return Response({'success': False, 'msg': '配方步序有误，炭黑称量列表中无炭黑！'})
        if oil_cnt and not add_oil_cnt:  # 有油料称量、无加油步序
            return Response({'success': False, 'msg': '配方步序有误，油料称量列表中有油料！'})
        if not oil_cnt and add_oil_cnt:  # 无油料称量，有加油料步序
            return Response({'success': False, 'msg': '配方步序有误，油料称量列表中无油料！'})
        if open_door_process:
            if not last_action_process:
                return Response({'success': False, 'msg': '步序错误,开卸料门动作之前必需要有条件！'})
            else:
                if open_door_process.sn <= last_action_process.sn:
                    return Response({'success': False, 'msg': "步序错误，开卸料门动作必需在条件 '{}' 之后！".format(last_action_process.condition.condition)})
        return Response({'success': True, 'msg': 'OK'})