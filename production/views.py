import datetime
import re

from django.db import connection
from django.db.models import Sum, Max, F, Value, CharField
from django.db.models.functions import Concat
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from django.db.transaction import atomic
from basics.models import PlanSchedule, Equip
from mes.common_code import CommonDeleteMixin, SqlClient
from mes.conf import EQUIP_LIST
from mes.derorators import api_recorder
from mes.paginations import SinglePageNumberPagination
from plan.models import ProductClassesPlan
from production.filters import TrainsFeedbacksFilter, PalletFeedbacksFilter, QualityControlFilter, EquipStatusFilter, \
    PlanStatusFilter, ExpendMaterialFilter, WeighParameterCarbonFilter, MaterialStatisticsFilter
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, ExpendMaterial, OperationLog, \
    QualityControl, MaterialTankStatus, IfupReportBasisBackups, IfupReportWeightBackups, IfupReportMixBackups, \
    ProcessFeedback
from production.serializers import QualityControlSerializer, OperationLogSerializer, ExpendMaterialSerializer, \
    PlanStatusSerializer, EquipStatusSerializer, PalletFeedbacksSerializer, TrainsFeedbacksSerializer, \
    ProductionRecordSerializer, MaterialTankStatusSerializer, \
    WeighInformationSerializer1, MixerInformationSerializer1, CurveInformationSerializer, MaterialStatisticsSerializer, \
    PalletSerializer, WeighInformationSerializer2, MixerInformationSerializer2, TrainsFeedbacksSerializer2
from production.utils import strtoint, gen_material_export_file_response
from recipe.models import ProductProcessDetail
import logging

logger = logging.getLogger('sync_log')


@method_decorator([api_recorder], name="dispatch")
class TrainsFeedbacksViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             GenericViewSet):
    """
    list:
        车次/批次产出反馈列表
    retrieve:
        车次/批次产出反馈详情
    create:
        创建车次/批次产出反馈
    """
    queryset = TrainsFeedbacks.objects.filter(delete_flag=False)
    # model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TrainsFeedbacksSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = TrainsFeedbacksFilter

    def list(self, request, *args, **kwargs):
        actual_trains = request.query_params.get("actual_trains", '')
        if "," in actual_trains:
            train_list = actual_trains.split(",")
            try:
                queryset = self.filter_queryset(self.get_queryset().filter(actual_trains__gte=train_list[0],
                                                                           actual_trains__lte=train_list[-1]))
            except:
                return Response({"actual_trains": "请输入: <开始车次>,<结束车次>。这类格式"})
        else:
            queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class PalletFeedbacksViewSet(mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             GenericViewSet):
    """
        list:
            托盘产出反馈列表
        retrieve:
            托盘产出反馈详情
        create:
            托盘产出反馈反馈
    """
    queryset = PalletFeedbacks.objects.filter()
    # model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PalletFeedbacksSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter


@method_decorator([api_recorder], name="dispatch")
class PalletDetailViewSet(mixins.ListModelMixin,
                          GenericViewSet):
    """
        list:
            托盘产出反馈列表
        retrieve:
            托盘产出反馈详情
        create:
            托盘产出反馈反馈
    """
    queryset = PalletFeedbacks.objects.filter()
    permission_classes = ()
    serializer_class = PalletSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if queryset.exists():
            queryset = [queryset.order_by("product_time").last()]
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class EquipStatusViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """
    list:
        机台状况反馈列表
    retrieve:
        机台状况反馈详情
    create:
        创建机台状况反馈
    """
    queryset = EquipStatus.objects.filter(delete_flag=False)
    pagination_class = None
    # model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EquipStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = EquipStatusFilter


@method_decorator([api_recorder], name="dispatch")
class PlanStatusViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """
    list:
        计划状态变更列表
    retrieve:
        计划状态变更详情
    create:
        创建计划状态变更
    """
    queryset = PlanStatus.objects.filter(delete_flag=False)
    # model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PlanStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PlanStatusFilter


@method_decorator([api_recorder], name="dispatch")
class ExpendMaterialViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    """
    list:
        原材料消耗列表
    retrieve:
        原材料消耗详情
    create:
        创建原材料消耗
    """
    queryset = ExpendMaterial.objects.filter(delete_flag=False)
    # model_name = queryset.model.__name__.lower()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ExpendMaterialSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('id',)
    filter_class = ExpendMaterialFilter

    def _validate_params(self, params):
        for k, v in params.items():
            if not re.search(r"^[a-zA-Z0-9\u4e00-\u9fa5\-\s:.]+$", v):
                raise ValidationError(f"字段{k}的值{v}非规范输入，请规范后重试")

    def _get_sql(self, params):
        equip_no = params.get("equip_no")
        product_no = params.get("product_no")
        material_type = params.get("material_type")
        st = params.get("st")
        et = params.get("et")
        if equip_no or product_no or material_type or st or et:
            condition_str = "WHERE"
            if equip_no:
                if condition_str == "WHERE":
                    condition_str += f" equip_no='{equip_no}'"
                else:
                    condition_str += f" and equip_no='{equip_no}'"
            if material_type:
                if condition_str == "WHERE":
                    condition_str += f" material_type='{material_type}'"
                else:
                    condition_str += f" and material_type='{material_type}'"
            if product_no:
                if condition_str == "WHERE":
                    condition_str += f" product_no='{product_no}'"
                else:
                    condition_str += f" and product_no='{product_no}'"
            if st:
                if condition_str == "WHERE":
                    condition_str += f" product_time >= '{st}'"
                else:
                    condition_str += f" and product_time >= '{st}'"
            if et:
                if condition_str == "WHERE":
                    condition_str += f" product_time <= '{et}'"
                else:
                    condition_str += f" and product_time <= '{et}'"
        else:
            condition_str = ''
        sql_str = f"""select min(id) as id, equip_no, product_no, material_no, max(material_type) as material_type, 
                            max(material_name) as material_name, max(plan_classes_uid) as plan_classes_uid, 
                            SUM(expend_material.actual_weight / 100) as actual_weight 
                            from expend_material {condition_str} GROUP BY equip_no, product_no, material_no ORDER BY product_time;
                """
        return sql_str

    def list(self, request, *args, **kwargs):
        params = request.query_params
        page = int(params.get("page", 1))
        page_size = int(params.get("page_size", 10))
        if not 1 <= page <= 2 ** 16:
            raise ValidationError(f"页码:{page}错误")
        if not 10 <= page_size <= 1000:
            raise ValidationError(f"页长:{page_size}错误")
        # self._validate_params(params)
        sql_str = self._get_sql(params)
        em_set = ExpendMaterial.objects.raw(sql_str)
        count = len(em_set)
        rep_list = []
        for em in em_set:
            rep = {
                "id": em.id,
                "equip_no": em.equip_no,
                "product_no": em.product_no,
                "material_no": em.material_no,
                "material_type": em.material_type,
                "material_name": em.material_name,
                "actual_weight": em.actual_weight,
                "plan_classes_uid": em.plan_classes_uid
            }
            rep_list.append(rep)
        rep_list = rep_list[(page - 1) * page_size:page_size * page]
        return Response({"count": count, "results": rep_list})


@method_decorator([api_recorder], name="dispatch")
class OperationLogViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.ListModelMixin,
                          GenericViewSet):
    """
    list:
        操作日志列表
    retrieve:
        操作日志详情
    create:
        创建操作日志
    """
    queryset = OperationLog.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = OperationLogSerializer


@method_decorator([api_recorder], name="dispatch")
class QualityControlViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            GenericViewSet):
    """
    list:
        质检结果列表
    retrieve:
        质检结果详情
    create:
        创建质检结果
    """
    queryset = QualityControl.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = QualityControlSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = QualityControlFilter


@method_decorator([api_recorder], name="dispatch")
class PlanRealityViewSet(mixins.ListModelMixin,
                         GenericViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        search_time_str = params.get("search_time")
        target_equip_no = params.get('equip_no')
        if search_time_str:
            if not re.search(r"[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}", search_time_str):
                raise ValidationError("查询时间格式异常")
        else:
            search_time_str = str(datetime.date.today())
        if target_equip_no:
            pcp_set = ProductClassesPlan.objects.filter(product_day_plan__plan_schedule__day_time=search_time_str,
                                                        product_day_plan__equip__equip_no=target_equip_no,
                                                        delete_flag=False).select_related(
                'product_day_plan__equip__equip_no',
                'product_day_plan__product_batching__stage_product_batch_no',
                'product_day_plan_id', 'time', 'product_day_plan__product_batching__stage__global_name')
        else:
            pcp_set = ProductClassesPlan.objects.filter(product_day_plan__plan_schedule__day_time=search_time_str,
                                                        delete_flag=False).select_related(
                'product_day_plan__equip__equip_no',
                'product_day_plan__product_batching__stage_product_batch_no',
                'product_day_plan_id', 'time', 'product_day_plan__product_batching__stage__global_name')
        uid_list = pcp_set.values_list("plan_classes_uid", flat=True)
        day_plan_list = pcp_set.values_list("product_day_plan__id", flat=True)
        tf_set = TrainsFeedbacks.objects.values('plan_classes_uid').filter(plan_classes_uid__in=uid_list).annotate(
            actual_trains=Max('actual_trains'), actual_weight=Sum('actual_weight'), begin_time=Max('begin_time'),
            actual_time=Max('product_time'))
        tf_dict = {x.get("plan_classes_uid"): [x.get("actual_trains"), x.get("actual_weight"), x.get("begin_time"),
                                               x.get("actual_time")] for x in tf_set}
        day_plan_dict = {x: {"plan_weight": 0, "plan_trains": 0, "actual_trains": 0, "actual_weight": 0, "plan_time": 0,
                             "start_rate": None}
                         for x in day_plan_list}
        pcp_data = pcp_set.values("plan_classes_uid", "weight", "plan_trains", 'product_day_plan__equip__equip_no',
                                  'product_day_plan__product_batching__stage_product_batch_no',
                                  'product_day_plan_id', 'time',
                                  'product_day_plan__product_batching__stage__global_name')
        for pcp in pcp_data:
            day_plan_id = pcp.get('product_day_plan_id')
            plan_classes_uid = pcp.get('plan_classes_uid')
            day_plan_dict[day_plan_id].update(
                equip_no=pcp.get('product_day_plan__equip__equip_no'),
                product_no=pcp.get('product_day_plan__product_batching__stage_product_batch_no'),
                stage=pcp.get('product_day_plan__product_batching__stage__global_name'))
            day_plan_dict[day_plan_id]["plan_weight"] += pcp.get('weight', 0)
            day_plan_dict[day_plan_id]["plan_trains"] += pcp.get('plan_trains', 0)
            day_plan_dict[day_plan_id]["plan_time"] += pcp.get('time', 0)
            if not tf_dict.get(plan_classes_uid):
                day_plan_dict[day_plan_id]["actual_trains"] += 0
                day_plan_dict[day_plan_id]["actual_weight"] += 0
                day_plan_dict[day_plan_id]["begin_time"] = datetime.datetime.now()
                day_plan_dict[day_plan_id]["actual_time"] = datetime.datetime.now()
                continue
            day_plan_dict[day_plan_id]["actual_trains"] += tf_dict[plan_classes_uid][0]
            day_plan_dict[day_plan_id]["actual_weight"] += round(tf_dict[plan_classes_uid][1] / 100, 2)
            day_plan_dict[day_plan_id]["begin_time"] = tf_dict[plan_classes_uid][2]
            day_plan_dict[day_plan_id]["actual_time"] = tf_dict[plan_classes_uid][3]
        temp_data = {}
        for equip_no in EQUIP_LIST:
            temp_data[equip_no] = []
            for temp in day_plan_dict.values():
                if temp.get("equip_no") == equip_no:
                    temp_data[equip_no].append(temp)
        datas = []
        for equip_data in temp_data.values():
            equip_data.sort(key=lambda x: (x.get("equip_no"), x.get("begin_time")))
            new_equip_data = []
            for _ in equip_data:
                _.update(sn=equip_data.index(_) + 1)
                _.update(ach_rate=round(_.get('actual_trains') / _.get('plan_trains') * 100, 2))
                new_equip_data.append(_)
            datas += new_equip_data
        return Response({"data": datas})

    def list_bak(self, request, *args, **kwargs):
        # 获取url参数 search_time equip_no
        return_data = {
            "data": []
        }
        temp_data = {}
        params = request.query_params
        search_time_str = params.get("search_time")
        target_equip_no = params.get('equip_no')
        # 通过日期参数查工厂排班
        if search_time_str:
            if not re.search(r"[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}", search_time_str):
                return Response("bad search_time", status=400)
            plan_schedule = PlanSchedule.objects.filter(day_time=search_time_str).first()
        else:
            plan_schedule = PlanSchedule.objects.filter(delete_flag=False).first()
        # 通过排班查日计划
        if not plan_schedule:
            return Response(return_data)
        if target_equip_no:
            day_plan_set = plan_schedule.ps_day_plan.filter(delete_flag=False, equip__equip_no=target_equip_no)
        else:
            day_plan_set = plan_schedule.ps_day_plan.filter(delete_flag=False)
        datas = []
        for day_plan in list(day_plan_set):
            instance = {}
            plan_trains = 0
            actual_trains = 0
            plan_weight = 0
            actual_weight = 0
            plan_time = 0
            actual_time = 0
            begin_time = None
            product_no = day_plan.product_batching.stage_product_batch_no
            stage = day_plan.product_batching.stage.global_name
            equip_no = day_plan.equip.equip_no
            if equip_no not in temp_data:
                temp_data[equip_no] = []
            # 通过日计划id再去查班次计划
            class_plan_set = ProductClassesPlan.objects.filter(product_day_plan=day_plan.id).order_by("sn")
            # 若班次计划为空则不进行后续操作
            if not class_plan_set:
                continue
            for class_plan in list(class_plan_set):
                plan_trains += class_plan.plan_trains
                plan_weight += class_plan.weight
                plan_time += class_plan.total_time
                if target_equip_no:
                    temp_ret_set = TrainsFeedbacks.objects.filter(plan_classes_uid=class_plan.plan_classes_uid,
                                                                  equip_no=target_equip_no)
                else:
                    temp_ret_set = TrainsFeedbacks.objects.filter(plan_classes_uid=class_plan.plan_classes_uid)
                if temp_ret_set:
                    actual = temp_ret_set.order_by("-created_date").first()
                    actual_trains += actual.actual_trains
                    actual_weight += actual.actual_weight
                    actual_time = actual.time
                    begin_time = actual.begin_time
                else:
                    actual_trains += 0
                    actual_weight += 0
                    actual_time = 0
                    begin_time = None
            if plan_weight:
                ach_rate = actual_weight / plan_weight * 100
            else:
                ach_rate = 0
            instance.update(equip_no=equip_no, product_no=product_no,
                            plan_trains=plan_trains, actual_trains=actual_trains,
                            plan_weight=plan_weight, actual_weight=actual_weight,
                            plan_time=plan_time, actual_time=actual_time,
                            stage=stage, ach_rate=ach_rate,
                            start_rate=None, begin_time=begin_time)
            if equip_no in temp_data:
                temp_data[equip_no].append(instance)
        for equip_data in temp_data.values():
            equip_data.sort(key=lambda x: (x.get("equip_no"), x.get("begin_time")))
            new_equip_data = []
            for _ in equip_data:
                _.update(sn=equip_data.index(_) + 1)
                new_equip_data.append(_)
            datas += new_equip_data
        return_data["data"] = datas
        return Response(return_data)


@method_decorator([api_recorder], name="dispatch")
class ProductActualViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    """密炼实绩"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        params = request.query_params
        search_time_str = params.get("search_time")
        target_equip_no = params.get('equip_no')
        if search_time_str:
            if not re.search(r"[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}", search_time_str):
                raise ValidationError("查询时间格式异常")
        else:
            search_time_str = str(datetime.date.today())
        if target_equip_no:
            pcp_set = ProductClassesPlan.objects.filter(product_day_plan__plan_schedule__day_time=search_time_str,
                                                        product_day_plan__equip__equip_no=target_equip_no,
                                                        delete_flag=False).select_related(
                'product_day_plan__equip__equip_no',
                'product_day_plan__product_batching__stage_product_batch_no',
                'work_schedule_plan__classes__global_name',
                'product_day_plan_id')
        else:
            pcp_set = ProductClassesPlan.objects.filter(product_day_plan__plan_schedule__day_time=search_time_str,
                                                        delete_flag=False).select_related(
                'product_day_plan__equip__equip_no',
                'product_day_plan__product_batching__stage_product_batch_no',
                'work_schedule_plan__classes__global_name',
                'product_day_plan_id')
        uid_list = pcp_set.values_list("plan_classes_uid", flat=True)
        day_plan_list = pcp_set.values_list("product_day_plan__id", flat=True)
        tf_set = TrainsFeedbacks.objects.values('plan_classes_uid').filter(plan_classes_uid__in=uid_list).annotate(
            actual_trains=Max('actual_trains'), actual_weight=Sum('actual_weight'), classes=Max('classes'))
        tf_dict = {x.get("plan_classes_uid"): [x.get("actual_trains"), x.get("actual_weight"), x.get("classes")] for x
                   in tf_set}
        day_plan_dict = {x: {"plan_weight": 0, "plan_trains": 0, "actual_trains": 0, "actual_weight": 0,
                             "class_data": [None, None, None]}
                         for x in day_plan_list}
        pcp_data = pcp_set.values("plan_classes_uid", "weight", "plan_trains", 'product_day_plan__equip__equip_no',
                                  'product_day_plan__product_batching__stage_product_batch_no',
                                  'product_day_plan_id',
                                  'work_schedule_plan__classes__global_name')
        for pcp in pcp_data:
            class_name = pcp.get("work_schedule_plan__classes__global_name")
            day_plan_id = pcp.get('product_day_plan_id')
            plan_classes_uid = pcp.get('plan_classes_uid')
            day_plan_dict[day_plan_id].update(
                equip_no=pcp.get('product_day_plan__equip__equip_no'),
                product_no=pcp.get('product_day_plan__product_batching__stage_product_batch_no'))
            day_plan_dict[day_plan_id]["plan_weight"] += pcp.get('weight', 0)
            day_plan_dict[day_plan_id]["plan_trains"] += pcp.get('plan_trains', 0)
            if not tf_dict.get(plan_classes_uid):
                if class_name == "早班":
                    day_plan_dict[day_plan_id]["class_data"][0] = {
                        "plan_trains": pcp.get('plan_trains'),
                        "actual_trains": 0,
                        "classes": "早班"
                    }
                if class_name == "中班":
                    day_plan_dict[day_plan_id]["class_data"][1] = {
                        "plan_trains": pcp.get('plan_trains'),
                        "actual_trains": 0,
                        "classes": "中班"
                    }
                if class_name == "晚班":
                    day_plan_dict[day_plan_id]["class_data"][2] = {
                        "plan_trains": pcp.get('plan_trains'),
                        "actual_trains": 0,
                        "classes": "晚班"
                    }
                continue
            day_plan_dict[day_plan_id]["actual_trains"] += tf_dict[plan_classes_uid][0]
            day_plan_dict[day_plan_id]["actual_weight"] += round(tf_dict[plan_classes_uid][1] / 100, 2)
            if tf_dict[plan_classes_uid][2] == "早班":
                day_plan_dict[day_plan_id]["class_data"][0] = {
                    "plan_trains": pcp.get('plan_trains'),
                    "actual_trains": tf_dict[plan_classes_uid][0],
                    "classes": "早班"
                }
            if tf_dict[plan_classes_uid][2] == "中班":
                day_plan_dict[day_plan_id]["class_data"][1] = {
                    "plan_trains": pcp.get('plan_trains'),
                    "actual_trains": tf_dict[pcp.plan_classes_uid][0],
                    "classes": "中班"
                }
            if tf_dict[plan_classes_uid][2] == "晚班":
                day_plan_dict[day_plan_id]["class_data"][2] = {
                    "plan_trains": pcp.get('plan_trains'),
                    "actual_trains": tf_dict[plan_classes_uid][0],
                    "classes": "晚班"
                }
        ret = {"data": [_ for _ in day_plan_dict.values()]}
        return Response(ret)

    def list_bak_1(self, request, *args, **kwargs):
        # 获取url参数 search_time equip_no
        return_data = {
            "data": []
        }
        params = request.query_params
        search_time_str = params.get("search_time")
        target_equip_no = params.get('equip_no')
        # 通过日期参数查工厂排班
        if search_time_str:
            if not re.search(r"[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}", search_time_str):
                return Response("bad search_time", status=400)
            plan_schedule = PlanSchedule.objects.filter(day_time=search_time_str).first()
        else:
            plan_schedule = PlanSchedule.objects.filter().first()
        if not plan_schedule:
            return Response(return_data)
        # 通过排班查日计划
        if target_equip_no:
            day_plan_set = plan_schedule.ps_day_plan.filter(delete_flag=False, equip__equip_no=target_equip_no)
        else:
            day_plan_set = plan_schedule.ps_day_plan.filter(delete_flag=False)
        for day_plan in list(day_plan_set):
            instance = {}
            plan_trains_all = 0
            plan_weight_all = 0
            actual_trains = 0
            plan_weight = 0
            product_no = day_plan.product_batching.stage_product_batch_no
            equip_no = day_plan.equip.equip_no
            day_plan_actual = [None, None, None]
            # 通过日计划id再去查班次计划
            class_plan_set = ProductClassesPlan.objects.filter(product_day_plan=day_plan.id)
            if not class_plan_set:
                continue
            for class_plan in list(class_plan_set):
                plan_trains = class_plan.plan_trains
                plan_trains_all += class_plan.plan_trains
                plan_weight = class_plan.weight
                plan_weight_all += class_plan.weight
                class_name = class_plan.work_schedule_plan.classes.global_name
                if target_equip_no:
                    temp_ret_set = TrainsFeedbacks.objects.filter(plan_classes_uid=class_plan.plan_classes_uid,
                                                                  equip_no=target_equip_no)
                else:
                    temp_ret_set = TrainsFeedbacks.objects.filter(plan_classes_uid=class_plan.plan_classes_uid)
                if temp_ret_set:
                    actual = temp_ret_set.order_by("-created_date").first()
                    temp_class_actual = {
                        "plan_trains": plan_trains,
                        "actual_trains": actual.actual_trains,
                        "classes": class_name
                    }
                    if class_name == "早班":
                        day_plan_actual[0] = temp_class_actual
                    elif class_name == "中班":
                        day_plan_actual[1] = temp_class_actual
                    elif class_name == "晚班":
                        day_plan_actual[2] = temp_class_actual
                    else:
                        day_plan_actual.append(temp_class_actual)
                    actual_trains += actual.actual_trains
                else:
                    temp_class_actual = {
                        "plan_trains": plan_trains,
                        "actual_trains": 0,
                        "classes": class_name}
                    if class_name == "早班":
                        day_plan_actual[0] = temp_class_actual
                    elif class_name == "中班":
                        day_plan_actual[1] = temp_class_actual
                    elif class_name == "晚班":
                        day_plan_actual[2] = temp_class_actual
                    else:
                        day_plan_actual.append(temp_class_actual)
                    actual_trains += 0
            instance.update(classes_data=day_plan_actual, plan_weight=plan_weight_all,
                            product_no=product_no, equip_no=equip_no,
                            plan_trains=plan_trains_all, actual_trains=actual_trains)
            return_data["data"].append(instance)
        return Response(return_data)


@method_decorator([api_recorder], name="dispatch")
class ProductionRecordViewSet(mixins.ListModelMixin,
                              GenericViewSet):
    queryset = PalletFeedbacks.objects.filter()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ProductionRecordSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter


def send_cd_cil(equip_no, tank_type, model_name):
    # 发送油料炭黑数据给易控组态
    equip_no_int = int("".join(list(filter(str.isdigit, equip_no))))
    mts_set = MaterialTankStatus.objects.filter(tank_type=tank_type, equip_no=equip_no)
    sql = f"delete from {model_name} where machineno={equip_no_int} and matname!='卸料'"
    sc = SqlClient(sql=sql, equip_no=str(equip_no_int), user="sa", host="10.4.14.101", password="123", db="GZSFJ")
    sc.save()
    sc.close()
    sql1 = f'''insert into {model_name} (matname,matno,code,machineno,flag) values '''
    mts_list = []
    for mts_obj in mts_set:
        mts = f"('{mts_obj.material_name}', {int(mts_obj.tank_no)}, 2, {equip_no_int}, 1)"
        mts_list.append(mts)
        mts_values = ','.join(mts_list)
        sql2 = sql1 + mts_values
    sc1 = SqlClient(sql=sql2, equip_no=str(equip_no_int), user="sa", host="10.4.14.101", password="123", db="GZSFJ")
    sc1.save()
    sc1.close()


def send_cd_cil_sum(equip_no, tank_type, model_name, mattype):
    # 发送油料炭黑数据给易控组态
    equip_no_int = int("".join(list(filter(str.isdigit, equip_no))))
    mts_set = MaterialTankStatus.objects.filter(tank_type=tank_type, equip_no=equip_no)
    sql1 = f'''insert into {model_name} (latesttime,matname,matno,mattype,machineno,flag) values '''
    mts_list = []
    for mts_obj in mts_set:
        sql3 = f"""select * from {model_name} where machineno={equip_no_int} and matname='{mts_obj.material_name}'"""
        sc = SqlClient(sql=sql3, equip_no=str(equip_no_int), user="sa", host="10.4.14.101", password="123", db="GZSFJ")
        if sc.cursor.fetchall():
            sc.save()
            sc.close()
            continue
        mts = f"""('{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}','{mts_obj.material_name}', {int(mts_obj.tank_no)},'{mattype}', {equip_no_int}, 1)"""
        mts_list.append(mts)
        mts_values = ','.join(mts_list)
        sql2 = sql1 + mts_values
    if mts_list:
        sc1 = SqlClient(sql=sql2, equip_no=str(equip_no_int), user="sa", host="10.4.14.101", password="123", db="GZSFJ")
        sc1.save()
        sc1.close()


@method_decorator([api_recorder], name="dispatch")
class WeighParameterCarbonViewSet(CommonDeleteMixin, ModelViewSet):
    queryset = MaterialTankStatus.objects.filter(delete_flag=False, tank_type="1")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialTankStatusSerializer
    pagination_class = SinglePageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = WeighParameterCarbonFilter

    @atomic()
    def put(self, request, *args, **kwargs):
        data = request.data
        for i in data:
            id = i.get("id")
            # id = i['id']
            obj = MaterialTankStatus.objects.get(pk=id)
            obj.tank_name = i.get("tank_name")
            obj.material_no = i.get("material_no")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.save()
            # 发送炭黑数据给易控组态
            try:
                send_cd_cil(equip_no=obj.equip_no, tank_type=1, model_name='chbt_no_cb')
                send_cd_cil_sum(equip_no=obj.equip_no, tank_type=1, model_name='sum_mat_cb', mattype='C')
            except Exception as e:
                logger.error(e)
                raise ValidationError(f'{obj.equip_no}机台网络连接异常')
        return Response("ok", status=status.HTTP_201_CREATED)


@method_decorator([api_recorder], name="dispatch")
class WeighParameterFuelViewSet(mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    queryset = MaterialTankStatus.objects.filter(delete_flag=False, tank_type="2")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialTankStatusSerializer
    pagination_class = SinglePageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = WeighParameterCarbonFilter

    @atomic()
    def put(self, request, *args, **kwargs):
        data = request.data
        for i in data:
            id = i.get("id")
            obj = MaterialTankStatus.objects.get(pk=i.get("id"))
            obj.tank_name = i.get("tank_name")
            obj.material_no = i.get("material_no")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.save()
            # 发送油料数据给易控组态
            try:
                send_cd_cil(equip_no=obj.equip_no, tank_type=2, model_name='chbt_no_oil1')
                send_cd_cil_sum(equip_no=obj.equip_no, tank_type=2, model_name='sum_mat_oil', mattype='O')
            except Exception as e:
                logger.error(e)
                raise ValidationError(f'{obj.equip_no}机台网络连接异常')
        return Response("ok", status=status.HTTP_201_CREATED)


@method_decorator([api_recorder], name="dispatch")
class MaterialStatisticsViewSet(mixins.ListModelMixin,
                                GenericViewSet):
    queryset = ExpendMaterial.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialStatisticsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = MaterialStatisticsFilter


@method_decorator([api_recorder], name="dispatch")
class EquipStatusPlanList(APIView):
    """主页面展示"""
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):

        equip_nos = Equip.objects.filter(use_flag=True, category__equip_type__global_name="密炼设备").order_by(
            'equip_no').values_list('equip_no', flat=True)

        # 计划数据，根据设备机台号和班次分组，
        plan_set = ProductClassesPlan.objects.filter(
            work_schedule_plan__plan_schedule__day_time=datetime.datetime.now().date(),
            product_day_plan__equip__equip_no__in=list(equip_nos)
        )
        plan_data = plan_set.values('work_schedule_plan__classes__global_name',
                                    'product_day_plan__equip__equip_no').annotate(plan_num=Sum('plan_trains'))
        plan_uid = plan_set.values_list("plan_classes_uid", flat=True)
        plan_data = {item['product_day_plan__equip__equip_no'] + item['work_schedule_plan__classes__global_name']: item
                     for item in plan_data}

        # 先按照计划uid分组，取出最大的一条实际数据
        max_ids = TrainsFeedbacks.objects.filter(
            # created_date__date=datetime.datetime.now().date(),
            plan_classes_uid__in=plan_uid
        ).values('plan_classes_uid').annotate(max_id=Max('id')).values_list('max_id', flat=True)
        # 实际数据，根据设备机台号和班次分组，
        actual_data = TrainsFeedbacks.objects.filter(
            id__in=max_ids).values('equip_no', 'classes').annotate(
            actual_num=Sum('actual_trains'),
            ret=Max(Concat(F('equip_no'), Value(","),
                           F('created_date'), Value(","),
                           F('product_no'), output_field=CharField()
                           )))
        actual_data = {item['equip_no'] + item['classes']: item for item in actual_data}

        # 机台反馈数据
        equip_status_data = EquipStatus.objects.filter(
            created_date__date=datetime.datetime.now().date()
        ).values('equip_no').annotate(ret=Max(Concat(F('equip_no'), Value(","),
                                                     F('created_date'), Value(","),
                                                     F('current_trains'), Value(','),
                                                     F('status')), output_field=CharField()))
        equip_status_data = {item['equip_no']: item for item in equip_status_data}

        ret_data = {item: [] for item in equip_nos}

        class_dict = {'早班': 1, '中班': 2, '晚班': 3}
        for key, value in plan_data.items():
            class_name = value['work_schedule_plan__classes__global_name']
            equip_no = value['product_day_plan__equip__equip_no']
            classes_id = class_dict[class_name]
            plan_num = value['plan_num']
            if key in actual_data:
                actual_ret = actual_data[key]['ret'].split(',')
                actual_num = actual_data[key]['actual_num']
                es_ret = None
                if equip_no in equip_status_data:
                    es_ret = equip_status_data[equip_no]['ret'].split(',')
                ret_data[equip_no].append(
                    {"classes_id": classes_id,
                     "global_name": class_name,
                     "plan_num": plan_num,
                     "actual_num": actual_num,
                     'ret': [actual_ret[2], es_ret[2], es_ret[3]] if es_ret else [actual_ret[2], '--', '--']
                     }
                )
            else:
                ret_data[equip_no].append(
                    {"classes_id": classes_id,
                     "global_name": class_name,
                     "plan_num": plan_num,
                     "actual_num": 0,
                     'ret': []
                     }
                )
        return Response(ret_data)


@method_decorator([api_recorder], name="dispatch")
class EquipDetailedList(APIView):
    """主页面详情展示机"""

    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, *args, **kwargs):
        params = self.request.query_params
        equip_no = params.get('equip_no')
        product_no = params.get('product_no')
        ret_data = {}
        # 当前班次
        tfb_obj = TrainsFeedbacks.objects.filter(equip_no=equip_no, product_no=product_no, delete_flag=False).order_by(
            'created_date').last()
        if not tfb_obj:
            ret_data['classes_name'] = None
            ret_data['product_list'] = []
            ret_data['status_list'] = []
        else:
            ret_data['classes_name'] = tfb_obj.classes
            ret_data['product_list'] = []
            ret_data['status_list'] = []

        # 当前机台当前班次计划车次
        pcp_plan = ProductClassesPlan.objects.filter(delete_flag=False, product_day_plan__equip__equip_no=equip_no,
                                                     work_schedule_plan__plan_schedule__day_time=datetime.datetime.now().date(),
                                                     work_schedule_plan__classes__global_name=ret_data[
                                                         'classes_name']).values(
            'product_day_plan__product_batching__stage_product_batch_no').annotate(sum_plan_trains=Sum('plan_trains'))
        for pcp_dict in pcp_plan:
            product_dict = {}
            product_dict['product_no'] = pcp_dict['product_day_plan__product_batching__stage_product_batch_no']
            product_dict['sum_plan_trains'] = pcp_dict['sum_plan_trains']
            ret_data['product_list'].append(product_dict)

        # 当前机台当前班次实际车次
        max_ids = TrainsFeedbacks.objects.filter(
            equip_no=equip_no,
            classes=ret_data['classes_name'],
            created_date__date=datetime.datetime.now().date()
        ).values('plan_classes_uid').annotate(max_id=Max('id')).values_list('max_id', flat=True)
        actual_trains = TrainsFeedbacks.objects.filter(
            id__in=max_ids).values('product_no').annotate(actual_trains=Sum('actual_trains'))
        for product_dict in ret_data['product_list']:
            for actual_trains_dict in actual_trains:
                if product_dict['product_no'] == actual_trains_dict['product_no']:
                    product_dict['actual_trains'] = actual_trains_dict['actual_trains']

        # 机台状态统计
        air_status_list = f'''select
       equip_status.status,
       count(equip_status.status) as count_status
from equip_status
where equip_status.equip_no = '{equip_no}' and equip_status.delete_flag=FALSE and to_days(equip_status.created_date) = to_days(now())
group by equip_status.status;
'''
        cursor = connection.cursor()
        cursor.execute(air_status_list)
        status_list = cursor.fetchall()
        if not status_list:
            ret_data['status_list'] = []
        else:
            for _ in status_list:
                s_list = {}
                s_list['status'] = _[0]
                s_list['count_status'] = _[1]
                ret_data['status_list'].append(s_list)
        return Response(ret_data)


@method_decorator([api_recorder], name="dispatch")
class WeighInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """称量信息"""
    # queryset = ExpendMaterial.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # pagination_class = SinglePageNumberPagination
    # serializer_class = WeighInformationSerializer1
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 根据不同版本。返回不同数据
    def get_serializer_class(self):
        version = self.request.version
        if version == "v1":
            return WeighInformationSerializer1
        elif version == "v2":
            return WeighInformationSerializer2
        else:
            return WeighInformationSerializer1

    def get_queryset(self):
        version = self.request.version
        feed_back_id = self.request.query_params.get('feed_back_id')
        if version == "v2":
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irw_queryset = ExpendMaterial.objects.filter(equip_no=tfb_obk.equip_no,
                                                             plan_classes_uid=tfb_obk.plan_classes_uid,
                                                             product_no=tfb_obk.product_no,
                                                             trains=tfb_obk.actual_trains, delete_flag=False)
            except:
                raise ValidationError('车次产出反馈或车次报表材料重量没有数据')
        elif version == "v1":
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irw_queryset = IfupReportWeightBackups.objects.filter(机台号=strtoint(tfb_obk.equip_no),
                                                                      计划号=tfb_obk.plan_classes_uid,
                                                                      配方号=tfb_obk.product_no,
                                                                      车次号=tfb_obk.actual_trains)
            except:
                raise ValidationError('车次产出反馈或车次报表材料重量没有数据')
        else:
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irw_queryset = IfupReportWeightBackups.objects.filter(机台号=strtoint(tfb_obk.equip_no),
                                                                      计划号=tfb_obk.plan_classes_uid,
                                                                      配方号=tfb_obk.product_no,
                                                                      车次号=tfb_obk.actual_trains)
            except:
                raise ValidationError('车次产出反馈或车次报表材料重量没有数据')
        return irw_queryset


@method_decorator([api_recorder], name="dispatch")
class MixerInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """密炼信息"""
    # queryset = ProductProcessDetail.objects.filter(delete_flagflag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # pagination_class = SinglePageNumberPagination
    # serializer_class = MixerInformationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 根据不同版本。返回不同数据
    def get_serializer_class(self):
        version = self.request.version
        if version == "v1":
            return MixerInformationSerializer1
        elif version == "v2":
            return MixerInformationSerializer2
        else:
            return MixerInformationSerializer1

    def get_queryset(self):
        version = self.request.version
        feed_back_id = self.request.query_params.get('feed_back_id')
        if version == "v2":
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irm_queryset = ProcessFeedback.objects.filter(plan_classes_uid=tfb_obk.plan_classes_uid,
                                                              equip_no=tfb_obk.equip_no,
                                                              product_no=tfb_obk.product_no,
                                                              current_trains=tfb_obk.actual_trains
                                                              )
            except:
                raise ValidationError('车次产出反馈或胶料配料标准步序详情没有数据')
        elif version == "v1":
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irm_queryset = IfupReportMixBackups.objects.filter(机台号=strtoint(tfb_obk.equip_no),
                                                                   计划号=tfb_obk.plan_classes_uid,
                                                                   配方号=tfb_obk.product_no,
                                                                   密炼车次=tfb_obk.actual_trains)
            except:
                raise ValidationError('车次产出反馈或车次报表步序表没有数据')
        else:
            try:
                tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
                irm_queryset = IfupReportMixBackups.objects.filter(机台号=strtoint(tfb_obk.equip_no),
                                                                   计划号=tfb_obk.plan_classes_uid,
                                                                   配方号=tfb_obk.product_no,
                                                                   密炼车次=tfb_obk.actual_trains)
            except:
                raise ValidationError('车次产出反馈或车次报表步序表没有数据')
        return irm_queryset


@method_decorator([api_recorder], name="dispatch")
class CurveInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """工艺曲线信息"""
    queryset = EquipStatus.objects.filter()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = SinglePageNumberPagination
    serializer_class = CurveInformationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def get_queryset(self):
        feed_back_id = self.request.query_params.get('feed_back_id')
        try:
            tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
            irc_queryset = EquipStatus.objects.filter(equip_no=tfb_obk.equip_no,
                                                      plan_classes_uid=tfb_obk.plan_classes_uid,
                                                      product_time__gte=tfb_obk.begin_time,
                                                      product_time__lte=tfb_obk.end_time).order_by('product_time')
        except:
            raise ValidationError('车次产出反馈或车次报表工艺曲线数据表没有数据')

        return irc_queryset


@method_decorator([api_recorder], name="dispatch")
class TrainsFeedbacksAPIView(mixins.ListModelMixin,
                             GenericViewSet):
    """车次报表展示接口"""
    queryset = TrainsFeedbacks.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = TrainsFeedbacksSerializer2
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filter_class = TrainsFeedbacksFilter

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == "v1":
            params = request.query_params
            begin_time = params.get("begin_time", None)
            end_time = params.get("end_time", None)
            equip_no = params.get("equip_no", None)
            product_no = params.get("product_no", None)
            try:
                page = int(params.get("page", 1))
                page_size = int(params.get("page_size", 10))
            except Exception as e:
                return Response("page和page_size必须是int", status=400)
            operation_user = params.get("operation_user", None)
            filter_dict = {}
            if begin_time:
                filter_dict['begin_time__gte'] = begin_time
            if end_time:
                filter_dict['end_time__lte'] = end_time
            if equip_no:
                filter_dict['equip_no'] = equip_no
            if product_no:
                filter_dict['product_no'] = product_no
            if operation_user:
                filter_dict['operation_user'] = operation_user

            tf_queryset = TrainsFeedbacks.objects.filter(**filter_dict).values()
            counts = tf_queryset.count()
            tf_queryset = tf_queryset[(page - 1) * page_size:page_size * page]
            for tf_obj in tf_queryset:
                production_details = {}
                # TODO 中间表
                irb_obj = IfupReportBasisBackups.objects.filter(机台号=strtoint(tf_obj['equip_no']),
                                                                计划号=tf_obj['plan_classes_uid'],
                                                                配方号=tf_obj['product_no'],
                                                                车次号=tf_obj['actual_trains']).order_by('存盘时间').last()
                if irb_obj:
                    production_details['控制方式'] = irb_obj.控制方式  # 本远控
                    production_details['作业方式'] = irb_obj.作业方式  # 手自动
                    production_details['总重量'] = irb_obj.总重量 / 100
                    production_details['排胶时间'] = irb_obj.排胶时间
                    production_details['排胶温度'] = irb_obj.排胶温度
                    production_details['排胶能量'] = irb_obj.排胶能量
                    production_details['员工代号'] = irb_obj.员工代号
                    production_details['存盘时间'] = irb_obj.存盘时间
                    production_details['间隔时间'] = irb_obj.间隔时间
                    production_details['密炼时间'] = datetime.datetime.strptime(irb_obj.存盘时间, "%Y-%m-%d %X") - tf_obj[
                        'begin_time']  # 暂时由存盘时间代替 后期需要确实是否是存盘时间-开始时间
                    tf_obj['production_details'] = production_details
                else:
                    tf_obj['production_details'] = None
                ps_obj = PlanStatus.objects.filter(equip_no=tf_obj['equip_no'],
                                                   plan_classes_uid=tf_obj['plan_classes_uid'],
                                                   product_no=tf_obj['product_no'],
                                                   actual_trains=tf_obj['actual_trains']).order_by(
                    'product_time').last()
                if ps_obj:
                    tf_obj['status'] = ps_obj.status
                else:
                    tf_obj['status'] = None
            return Response({'count': counts, 'results': tf_queryset})
        elif version == "v2":
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            params = request.query_params
            begin_time = params.get("begin_time", None)
            end_time = params.get("end_time", None)
            equip_no = params.get("equip_no", None)
            product_no = params.get("product_no", None)
            try:
                page = int(params.get("page", 1))
                page_size = int(params.get("page_size", 10))
            except Exception as e:
                return Response("page和page_size必须是int", status=400)
            operation_user = params.get("operation_user", None)
            filter_dict = {}
            if begin_time:
                filter_dict['begin_time__gte'] = begin_time
            if end_time:
                filter_dict['end_time__lte'] = end_time
            if equip_no:
                filter_dict['equip_no'] = equip_no
            if product_no:
                filter_dict['product_no'] = product_no
            if operation_user:
                filter_dict['operation_user'] = operation_user

            tf_queryset = TrainsFeedbacks.objects.filter(**filter_dict).values()
            counts = tf_queryset.count()
            tf_queryset = tf_queryset[(page - 1) * page_size:page_size * page]
            for tf_obj in tf_queryset:
                production_details = {}
                # TODO 中间表
                irb_obj = IfupReportBasisBackups.objects.filter(机台号=strtoint(tf_obj['equip_no']),
                                                                计划号=tf_obj['plan_classes_uid'],
                                                                配方号=tf_obj['product_no'],
                                                                车次号=tf_obj['actual_trains']).order_by('存盘时间').last()
                if irb_obj:
                    production_details['控制方式'] = irb_obj.控制方式  # 本远控
                    production_details['作业方式'] = irb_obj.作业方式  # 手自动
                    production_details['总重量'] = irb_obj.总重量 / 100
                    production_details['排胶时间'] = irb_obj.排胶时间
                    production_details['排胶温度'] = irb_obj.排胶温度
                    production_details['排胶能量'] = irb_obj.排胶能量
                    production_details['员工代号'] = irb_obj.员工代号
                    production_details['存盘时间'] = irb_obj.存盘时间
                    production_details['间隔时间'] = irb_obj.间隔时间
                    production_details['密炼时间'] = datetime.datetime.strptime(irb_obj.存盘时间, "%Y-%m-%d %X") - tf_obj[
                        'begin_time']  # 暂时由存盘时间代替 后期需要确实是否是存盘时间-开始时间
                    tf_obj['production_details'] = production_details
                else:
                    tf_obj['production_details'] = None
                ps_obj = PlanStatus.objects.filter(equip_no=tf_obj['equip_no'],
                                                   plan_classes_uid=tf_obj['plan_classes_uid'],
                                                   product_no=tf_obj['product_no'],
                                                   actual_trains=tf_obj['actual_trains']).order_by(
                    'product_time').last()
                if ps_obj:
                    tf_obj['status'] = ps_obj.status
                else:
                    tf_obj['status'] = None
            return Response({'count': counts, 'results': tf_queryset})


@method_decorator([api_recorder], name="dispatch")
class MaterialExport(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     GenericViewSet):
    queryset = ExpendMaterial.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ExpendMaterialSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('id',)
    filter_class = ExpendMaterialFilter

    def _validate_params(self, params):
        for k, v in params.items():
            if not re.search(r"^[a-zA-Z0-9\u4e00-\u9fa5\-\s:.]+$", v):
                raise ValidationError(f"字段{k}的值{v}非规范输入，请规范后重试")

    def _get_sql(self, params):
        equip_no = params.get("equip_no")
        product_no = params.get("product_no")
        material_type = params.get("material_type")
        st = params.get("st")
        et = params.get("et")
        if equip_no or product_no or material_type or st or et:
            condition_str = "WHERE"
            if equip_no:
                if condition_str == "WHERE":
                    condition_str += f" equip_no='{equip_no}'"
                else:
                    condition_str += f" and equip_no='{equip_no}'"
            if material_type:
                if condition_str == "WHERE":
                    condition_str += f" material_type='{material_type}'"
                else:
                    condition_str += f" and material_type='{material_type}'"
            if product_no:
                if condition_str == "WHERE":
                    condition_str += f" product_no='{product_no}'"
                else:
                    condition_str += f" and product_no='{product_no}'"
            if st:
                if condition_str == "WHERE":
                    condition_str += f" product_time >= '{st}'"
                else:
                    condition_str += f" and product_time >= '{st}'"
            if et:
                if condition_str == "WHERE":
                    condition_str += f" product_time <= '{et}'"
                else:
                    condition_str += f" and product_time <= '{et}'"
        else:
            condition_str = ''
        sql_str = f"""select min(id) as id, equip_no, product_no, material_no, max(material_type) as material_type, 
                            max(material_name) as material_name, max(plan_classes_uid) as plan_classes_uid, 
                            SUM(expend_material.actual_weight / 100) as actual_weight 
                            from expend_material {condition_str} GROUP BY equip_no, product_no, material_no ORDER BY product_time;
                """
        # return gen_material_export_file_response('导出', sql_str)

        return sql_str

    def list(self, request, *args, **kwargs):
        params = request.query_params
        page = int(params.get("page", 1))
        page_size = int(params.get("page_size", 10))
        if not 1 <= page <= 2 ** 16:
            raise ValidationError(f"页码:{page}错误")
        if not 10 <= page_size <= 1000:
            raise ValidationError(f"页长:{page_size}错误")
        self._validate_params(params)
        sql_str = self._get_sql(params)
        em_set = ExpendMaterial.objects.raw(sql_str)
        count = len(em_set)
        rep_list = []
        for em in em_set:
            rep = {
                "id": em.id,
                "equip_no": em.equip_no,
                "product_no": em.product_no,
                "material_no": em.material_no,
                "material_type": em.material_type,
                "material_name": em.material_name,
                "actual_weight": em.actual_weight,
                "plan_classes_uid": em.plan_classes_uid
            }
            rep_list.append(rep)
        rep_list = rep_list[(page - 1) * page_size:page_size * page]
        # return Response({"count": count, "results": rep_list})
        return gen_material_export_file_response("results", rep_list)
