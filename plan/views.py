import datetime
import json
from collections import OrderedDict

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
from mes.conf import VERSION_EQUIP
from mes.derorators import api_recorder
from plan.filters import ProductDayPlanFilter, PalletFeedbacksFilter
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded
from plan.serializers import UpRegulationSerializer, DownRegulationSerializer, UpdateTrainsSerializer, \
    PalletFeedbacksPlanSerializer, PlanReceiveSerializer, ProductDayPlanSerializer
from production.models import PlanStatus, TrainsFeedbacks
from production.utils import strtoint
# Create your views here.
from recipe.models import ProductProcess, ProductBatching
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
    queryset = ProductClassesPlan.objects.filter(delete_flag=False).order_by('-id', 'sn')
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


@method_decorator([api_recorder], name="dispatch")
class PlanStatusList(APIView):
    """计划管理当前机台计划展示"""

    def get(self, request):
        params = request.query_params
        equip_no = params.get('equip_no')
        ps_obj = PlanStatus.objects.filter(equip_no=equip_no).last()
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


@method_decorator([api_recorder], name="dispatch")
class StopPlan(APIView):
    """计划停止"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    @atomic()
    def get(self, request):
        version = request.version
        params = request.query_params
        plan_id = params.get("id")
        equip_no = params.get("equip_name", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
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
        if "0" in equip_no:
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
            except Exception as e:
                raise ValidationError(f"上辅机连接超时|{e}")
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


# @method_decorator([api_recorder], name="dispatch")
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
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no=equip_no,
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
            "tempuse": 0 if actual_product_process.temp_use_flag else 1,
            # 三区水温是否启用 国自(true:启用， false:停用)  万龙(0:三区水温启用， 1:三区水温停用)
            "usenot": 0 if actual_product_batching.used_type == 4 else 1,  # 配方是否启用 国自(4:启用， 其他数字:不可用)  万龙(0:启用， 1:停用)
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
                "type": "P",  # 胶料 P
                "recstatus": "等待"
            }
            datas.append(data)
        return datas

    def _map_RecipeMix(self, product_batching, product_process_details, equip_no):
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no=equip_no,
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
                "set_pres": int(ppd.rpm) if ppd.rpm else 0,
                "set_rota": ppd.pressure if ppd.pressure else 0.0,
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
            'lasttime': params.get("day_time", None),  # 班日期
            'planid': params.get("plan_classes_uid", None),  # 计划编号  plan_no
            'startime': params.get("begin_time", None),  # 开始时间
            'stoptime': params.get("end_time", None),  # 结束时间
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
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no=equip_no,
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
        data[
            "if_not"] = 0 if actual_product_process.reuse_flag else -1  # 是否回收  国自(true:回收， false:不回收)  万龙（0:回收， -1:不回收）
        data["rot_temp"] = actual_product_process.zz_temp
        data["shut_temp"] = actual_product_process.xlm_temp
        data["side_temp"] = actual_product_process.cb_temp
        data["temp_on_off"] = 0 if actual_product_process.temp_use_flag else 1
        data["sp_num"] = actual_product_process.sp_num
        # 三区水温是否启用 国自(true:启用， false:停用)  万龙(0:三区水温启用， 1:三区水温停用)
        data[
            "recipe_off"] = 0 if actual_product_batching.used_type == 4 else 1  # 配方是否启用 国自(4:启用， 其他数字:不可用)  万龙(0:启用， 1:停用)
        data["machineno"] = int(equip_no)
        return data

    def _map_cb(self, product_batching, product_batching_details, equip_no):
        datas = []
        product_batching_details = product_batching_details.filter(material__material_type__global_name="炭黑")
        sn = 0
        for pbd in product_batching_details:
            sn += 1
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = pbd.material.material_name
            data["set_weight"] = pbd.actual_weight
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = sn
            data["mattype"] = "C"  # 炭黑
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_oil(self, product_batching, product_batching_details, equip_no):
        datas = []
        product_batching_details = product_batching_details.filter(material__material_type__global_name="油料")
        sn = 0
        for pbd in product_batching_details:
            sn += 1
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = pbd.material.material_name
            data["set_weight"] = pbd.actual_weight
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = sn
            data["mattype"] = "O"  # 油料
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_ploy(self, product_batching, product_batching_details, equip_no):
        datas = []
        gum_list = GlobalCode.objects.filter(global_type__type_name="胶料").values_list("global_name", flat=True)
        product_batching_details = product_batching_details.filter(material__material_type__global_name__in=gum_list)
        sn = 0
        for pbd in product_batching_details:
            sn += 1
            data = OrderedDict()
            data["id"] = pbd.id
            data["matname"] = pbd.material.material_name
            data["set_weight"] = pbd.actual_weight
            data["error_allow"] = pbd.standard_error
            data["recipe_name"] = product_batching.stage_product_batch_no
            data["act_code"] = sn
            data["mattype"] = "P"  # 炭黑
            data["machineno"] = int(equip_no)
            datas.append(data)
        return datas

    def _map_weigh(self, product_batching, product_batching_details, equip_no):
        # 胶料，油料，炭黑的合表
        datas = self._map_ploy(product_batching, product_batching_details, equip_no) \
                + self._map_oil(product_batching, product_batching_details, equip_no) \
                + self._map_cb(product_batching, product_batching_details, equip_no)
        if not datas:
            raise ValidationError("胶料配料详情为空，该计划不可用")
        return datas

    def _map_mix(self, product_batching, product_process_details, equip_no):
        if product_batching.batching_type == 2:
            actual_product_batching = ProductBatching.objects.exclude(used_type=6).filter(delete_flag=False,
                                                                                          stage_product_batch_no=product_batching.stage_product_batch_no,
                                                                                          equip__equip_no=equip_no,
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
        return datas

    def _map_plan(self, params, pcp_obj, equip_no):
        data = OrderedDict()
        data['id'] = pcp_obj.id  # id
        data['recipe_name'] = params.get("stage_product_batch_no", None)  # 配方名
        data['recipe_code'] = params.get("stage_product_batch_no", None)  # 配方编号
        data['latesttime'] = params.get("created_date", None)  # 计划创建时间
        data['planid'] = params.get("plan_classes_uid", None)  # 计划编号  plan_no
        data['starttime'] = params.get("begin_time", None)  # 开始时间
        data['stoptime'] = params.get("end_time", None)  # 结束时间
        data['grouptime'] = params.get("classes", None)  # 班次
        data['groupoper'] = params.get("group", None)  # 班组????
        data['setno'] = params.get("plan_trains", 1)  # 设定车次
        data['actno'] = 0,  # 当前车次
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
            raise ValidationError("该配方已存在于上辅机，请勿重复下达")
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
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")
        if not status:
            raise ValidationError(f"配方称量下达失败:{text}")
        mix = self._map_mix(product_batching, product_process_details, ext_str)
        mix_data = {"json": json.dumps({"datas": mix}, cls=DecimalEncoder)}
        try:
            status, text = WebService.issue(mix_data, 'recipe_step', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方步序已存在于上辅机，请勿重复下达")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")
        if not status:
            raise ValidationError(f"配方步序下达失败:{text}")
        plan = self._map_plan(params, pcp_obj, ext_str)
        try:
            status, text = WebService.issue(plan, 'plan', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该计划已存在于上辅机，请勿重复下达")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")
        if not status:
            raise ValidationError(f"计划下达失败:{text}")

    def _sync_update_interface(self, args, params=None, ext_str="", equip_no=""):
        product_batching, product_batching_details, product_process, product_process_details, pcp_obj = args
        recipe = self._map_recipe(pcp_obj, product_process, product_batching, ext_str)
        try:
            status, text = WebService.issue(recipe, 'recipe_con_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方不存在于上辅机，请检查上辅机")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")

        if not status:
            raise ValidationError(f"主配方重传失败:{text}")
        weigh = self._map_weigh(product_batching, product_batching_details, ext_str)
        weigh_data = {"json": json.dumps({"datas": weigh}, cls=DecimalEncoder)}  # 这是易控那边为获取批量数据约定的数据格式
        try:
            status, text = WebService.issue(weigh_data, 'recipe_weight_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方称量不存在于上辅机，请检查上辅机")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")
        if not status:
            raise ValidationError(f"配方称量重传失败:{text}")
        mix = self._map_mix(product_batching, product_process_details, ext_str)
        mix_data = {"json": json.dumps({"datas": mix}, cls=DecimalEncoder)}
        try:
            status, text = WebService.issue(mix_data, 'recipe_step_again', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            raise ValidationError("该配方步序不存在于上辅机，请检查上辅机")
        except:
            raise ValidationError(f"{equip_no} 网络连接异常")
        if not status:
            raise ValidationError(f"配方步序重传失败:{text}")

    @atomic()
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
        if "0" in equip_no:
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
        else:
            self._sync(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str, equip_no=equip_no)
            ps_obj.status = '已下达'
            ps_obj.save()
            pcp_obj.status = '已下达'
            pcp_obj.save()
            # self.send_to_yikong(params, pcp_obj)
        return Response({'_': '下达成功'}, status=200)

    @atomic()
    def put(self, request):
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
        if version == "v1":
            self._sync_update(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                              equip_no=equip_no)
        elif version == "v2":
            self._sync_update_interface(self.plan_recipe_integrity_check(pcp_obj), params=params, ext_str=ext_str,
                                        equip_no=equip_no)
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
