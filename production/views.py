import datetime
import json
import logging
import re
from decimal import Decimal
from io import BytesIO

import requests
import xlwt
from django.db import connection
from django.db.models import Sum, Max, Avg, F, Q
from django.db.transaction import atomic
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, APIException
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from basics.models import PlanSchedule, Equip, GlobalCodeType
from mes.common_code import CommonDeleteMixin, WebService
from mes.conf import EQUIP_LIST, VERSION_EQUIP
from mes.derorators import api_recorder
from mes.paginations import SinglePageNumberPagination
from mes.settings import MES_URL, DEBUG
from plan.models import ProductClassesPlan
from production.filters import TrainsFeedbacksFilter, PalletFeedbacksFilter, QualityControlFilter, EquipStatusFilter, \
    PlanStatusFilter, ExpendMaterialFilter, WeighParameterCarbonFilter, MaterialStatisticsFilter
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, ExpendMaterial, OperationLog, \
    QualityControl, MaterialTankStatus, IfupReportBasisBackups, IfupReportWeightBackups, IfupReportMixBackups, \
    ProcessFeedback, AlarmLog, FeedingMaterialLog, LoadMaterialLog, LoadTankMaterialLog, ManualInputTrains, \
    OtherMaterialLog, BatchScanLog
from production.serializers import QualityControlSerializer, OperationLogSerializer, \
    PlanStatusSerializer, EquipStatusSerializer, PalletFeedbacksSerializer, TrainsFeedbacksSerializer, \
    ProductionRecordSerializer, MaterialTankStatusSerializer, \
    WeighInformationSerializer1, MixerInformationSerializer1, CurveInformationSerializer, \
    MaterialStatisticsSerializer, PalletSerializer, WeighInformationSerializer2, \
    MixerInformationSerializer2, TrainsFeedbacksSerializer2, AlarmLogSerializer, ExpendMaterialSerializer2
from production.utils import strtoint, send_msg_to_terminal
from recipe.models import ProductBatchingMixed, Material, ProductBatchingDetailPlan, ProductBatching

logger = logging.getLogger('api_log')
error_log = logging.getLogger('error_log')


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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
    serializer_class = PalletFeedbacksSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter

    @action(methods=['post'], detail=False, permission_classes=[], url_path='bind-rfid',
            url_name='bind-rfid')
    def bind_rfid(self, request):
        try:
            requests.post(MES_URL+'api/v1/production/pallet-feedbacks/bind-rfid/',
                          json=request.data)
        except Exception:
            pass
        return Response('ok')


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
    authentication_classes = ()
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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
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
    permission_classes = ()
    authentication_classes = ()
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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
    serializer_class = ExpendMaterialSerializer2
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('id',)
    filter_class = ExpendMaterialFilter

    def export_xls(self, result):
        response = HttpResponse(content_type='application/vnd.ms-excel')
        filename = '物料统计报表'
        response['Content-Disposition'] = u'attachment;filename= ' + filename.encode('gbk').decode(
            'ISO-8859-1') + '.xls'
        # 创建一个文件对象
        wb = xlwt.Workbook(encoding='utf8')
        # 创建一个sheet对象
        sheet = wb.add_sheet('出入库信息', cell_overwrite_ok=True)
        style = xlwt.XFStyle()
        style.alignment.wrap = 1

        columns = ['机台', '配方', '物料类别', '物料名称', '实际重量']
        # 写入文件标题
        for col_num in range(len(columns)):
            sheet.write(0, col_num, columns[col_num])
            # 写入数据
        data_row = 1
        for i in result:
            sheet.write(data_row, 0, i['equip_no'])
            sheet.write(data_row, 1, i['product_no'])
            sheet.write(data_row, 2, i['material_type'])
            sheet.write(data_row, 3, i['material_name'])
            sheet.write(data_row, 4, i['actual_weight'])
            data_row = data_row + 1
        # 写出到IO
        output = BytesIO()
        wb.save(output)
        # 重新定位到开始
        output.seek(0)
        response.write(output.getvalue())
        return response

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        material_type_dict = dict(Material.objects.filter(delete_flag=False).values_list('material_name', 'material_type__global_name'))
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self,
            'material_type_dict': material_type_dict
        }

    def list(self, request, *args, **kwargs):
        export = self.request.query_params.get('export')
        material_type = self.request.query_params.get('material_type')
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.values('equip_no', 'product_no', 'material_no', 'material_name').order_by('equip_no', 'product_no').annotate(actual_weight=Sum('actual_weight')/100)
        data = self.get_serializer(queryset, many=True).data
        if material_type:
            data = list(filter(lambda x: x['material_type'] == material_type, data))
        page = self.paginate_queryset(data)
        if export:
            return self.export_xls(data)
        return self.get_paginated_response(page)


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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
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
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    permission_classes = ()
    authentication_classes = ()
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
                if class_name == "夜班":
                    day_plan_dict[day_plan_id]["class_data"][2] = {
                        "plan_trains": pcp.get('plan_trains'),
                        "actual_trains": 0,
                        "classes": "夜班"
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
            if tf_dict[plan_classes_uid][2] == "夜班":
                day_plan_dict[day_plan_id]["class_data"][2] = {
                    "plan_trains": pcp.get('plan_trains'),
                    "actual_trains": tf_dict[plan_classes_uid][0],
                    "classes": "夜班"
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
                    elif class_name == "夜班":
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
                    elif class_name == "夜班":
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


def send_cd_cil(equip_no, user_name):
    # 发送油料、炭黑以及称量信息数据给易控组态
    equip_no_int = int("".join(list(filter(str.isdigit, equip_no))))
    date_dict = {"json": {'data': []}}
    tank_list = ['1', '2']
    for tank_type in tank_list:
        mts_set = MaterialTankStatus.objects.filter(tank_type=tank_type, equip_no=equip_no)
        for mts_obj in mts_set:
            if mts_obj.tank_no == "卸料":
                continue
            line_no = mts_obj.line_no
            if line_no == 2:
                matname = '油料{}罐{}'.format(str(line_no), mts_obj.tank_no) if mts_obj.tank_type == '2' else "炭黑罐{}".format(mts_obj.tank_no)
            else:
                matname = "油料罐{}".format(mts_obj.tank_no) if mts_obj.tank_type == '2' else "炭黑罐{}".format(mts_obj.tank_no)
            mts_dict = {"latesttime": None,
                        "oper": user_name,
                        "matno": int(mts_obj.tank_no),
                        "matname": matname,
                        "matcode": mts_obj.material_name,
                        "slow": str(mts_obj.low_value),
                        "shark": str(mts_obj.advance_value),
                        "adjust": str(mts_obj.adjust_value),
                        "sharktime": str(mts_obj.dot_time),
                        "fast_speed": str(mts_obj.fast_speed),
                        "slow_speed": str(mts_obj.low_speed),
                        "machineno": equip_no_int,
                        "choices": '3' if line_no == 2 else tank_type,
                        'matplace': mts_obj.provenance if mts_obj.provenance else " "}
            date_dict['json']['data'].append(mts_dict)
    data = json.dumps(date_dict['json'])
    date_dict['json'] = data
    WebService.issue(date_dict, 'collect_weigh_parameter_service', equip_no=str(equip_no_int), equip_name="上辅机")


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
            if float(i.get("advance_value")) < 0.00 or float(i.get("advance_value")) > 5.00:
                raise ValidationError("提前量值必须在[0.00,5.00]之间，，请修正后重试")
            if float(i.get("low_value")) < 0.00 or float(i.get("low_value")) > 5.00:
                raise ValidationError("慢称值必须在[0.00,5.00]之间，请修正后重试")
            obj = MaterialTankStatus.objects.get(pk=id)
            obj.tank_name = i.get("tank_name")
            obj.material_name = i.get("material_name1")
            obj.material_no = i.get("material_no")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.provenance = i.get("provenance")
            obj.last_updated_user = self.request.user
            obj.save()
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
        equip_no = None
        for i in data:
            id = i.get("id")
            if float(i.get("advance_value")) < 0.00 or float(i.get("advance_value")) > 5.00:
                raise ValidationError("提前量值必须在[0.00,5.00]之间，请修正后重试")
            if float(i.get("low_value")) < 0.00 or float(i.get("low_value")) > 5.00:
                raise ValidationError("慢称值必须在[0.00,5.00]之间，请修正后重试")
            obj = MaterialTankStatus.objects.get(pk=i.get("id"))
            obj.tank_name = i.get("tank_name")
            obj.material_name = i.get("material_name1")
            obj.material_no = i.get("material_no")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.provenance = i.get("provenance")
            obj.last_updated_user = self.request.user
            obj.save()
            # 发送油料数据给易控组态
            equip_no = obj.equip_no
        if not DEBUG:
            try:
                send_cd_cil(equip_no=equip_no, user_name=request.user.username)
            except Exception as e:
                logger.error(e)
                raise ValidationError(f'{equip_no}机台网络连接异常')
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
        class_dict = {'早班': 1, '中班': 2, '夜班': 3}
        ret = {}
        for equip_no in equip_nos:
            last_plan_status = PlanStatus.objects.filter(equip_no=equip_no,
                                                         status='运行中').order_by('created_date').last()
            if last_plan_status:
                plan = ProductClassesPlan.objects.filter(plan_classes_uid=last_plan_status.plan_classes_uid).first()
                last_trains_feedback = TrainsFeedbacks.objects.filter(plan_classes_uid=last_plan_status.plan_classes_uid
                                                                      ).order_by('created_date').last()
                actual_trains = last_trains_feedback.actual_trains if last_trains_feedback else 0
                if plan:
                    ret[equip_no] = [(
                        {"classes_id": class_dict[plan.work_schedule_plan.classes.global_name],
                         "global_name": plan.work_schedule_plan.classes.global_name,
                         "plan_num": plan.plan_trains,
                         "actual_num": actual_trains,
                         'ret': [last_plan_status.product_no, actual_trains, '运行中']
                         }
                    )]
                else:
                    ret[equip_no] = []
            else:
                ret[equip_no] = []
        return Response(ret)


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
        tfb_obj = TrainsFeedbacks.objects.filter(equip_no=equip_no, product_no=product_no,
                                                 delete_flag=False).order_by(
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
            'product_day_plan__product_batching__stage_product_batch_no').annotate(
            sum_plan_trains=Sum('plan_trains'))
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    # 根据不同版本。返回不同数据
    def get_serializer_class(self):
        version = self.request.version
        params = self.request.query_params
        equip_no = params.get("equip_no", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
        if version == "v1":
            return WeighInformationSerializer1
        elif version == "v2":
            return WeighInformationSerializer2
        else:
            return WeighInformationSerializer2

    def get_queryset(self):
        version = self.request.version
        params = self.request.query_params
        equip_no = params.get("equip_no", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
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
                irw_queryset = ExpendMaterial.objects.filter(equip_no=tfb_obk.equip_no,
                                                             plan_classes_uid=tfb_obk.plan_classes_uid,
                                                             product_no=tfb_obk.product_no,
                                                             trains=tfb_obk.actual_trains, delete_flag=False)
            except:
                raise ValidationError('车次产出反馈或车次报表材料重量没有数据')
        return irw_queryset


@method_decorator([api_recorder], name="dispatch")
class MixerInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """密炼信息"""
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = SinglePageNumberPagination

    # 根据不同版本。返回不同数据
    def get_serializer_class(self):
        version = self.request.version
        params = self.request.query_params
        equip_no = params.get("equip_no", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
        if version == "v1":
            return MixerInformationSerializer1
        elif version == "v2":
            return MixerInformationSerializer2
        else:
            return MixerInformationSerializer2

    def get_queryset(self):
        version = self.request.version
        feed_back_id = self.request.query_params.get('feed_back_id')
        params = self.request.query_params
        equip_no = params.get("equip_no", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
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
                irm_queryset = ProcessFeedback.objects.filter(plan_classes_uid=tfb_obk.plan_classes_uid,
                                                              equip_no=tfb_obk.equip_no,
                                                              product_no=tfb_obk.product_no,
                                                              current_trains=tfb_obk.actual_trains
                                                              )
            except:
                raise ValidationError('车次产出反馈或胶料配料标准步序详情没有数据')
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
            if tfb_obk.equip_no == "Z04":
                mixer = tfb_obk.operation_user
                if mixer == "Mixer1":
                    mixer_id = 1
                elif mixer == "Mixer2":
                    mixer_id = 2
                else:
                    mixer_id = 2
                irc_queryset = EquipStatus.objects.filter(equip_no=tfb_obk.equip_no,
                                                          plan_classes_uid=tfb_obk.plan_classes_uid,
                                                          current_trains=tfb_obk.actual_trains,
                                                          delete_user_id=mixer_id).order_by('product_time')
            else:
                irc_queryset = EquipStatus.objects.filter(equip_no=tfb_obk.equip_no,
                                                          plan_classes_uid=tfb_obk.plan_classes_uid,
                                                          product_time__gte=tfb_obk.begin_time,
                                                          product_time__lte=tfb_obk.end_time).order_by('product_time')
        except:
            raise ValidationError('车次产出反馈或车次报表工艺曲线数据表没有数据')

        return irc_queryset


@method_decorator([api_recorder], name="dispatch")
class AlarmLogList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                   GenericViewSet):
    """报警信息"""
    queryset = AlarmLog.objects.filter()
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = AlarmLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def get_queryset(self):
        feed_back_id = self.request.query_params.get('feed_back_id')
        try:
            tfb_obk = TrainsFeedbacks.objects.get(id=feed_back_id)
            al_queryset = AlarmLog.objects.filter(equip_no=tfb_obk.equip_no,
                                                  product_time__gte=tfb_obk.begin_time,
                                                  product_time__lte=tfb_obk.end_time).order_by('product_time')
        except:
            raise ValidationError('报警日志没有数据')

        return al_queryset


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
        params = request.query_params
        equip_no = params.get("equip_no", None)
        if not equip_no:
            raise ValidationError('机台号必传')
        version = VERSION_EQUIP[equip_no]
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
            tf_queryset = list(tf_queryset)
            tf_queryset.append({'version': 'v1'})
            return Response({'count': counts, 'results': tf_queryset})
        elif version == "v2":
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data_list = serializer.data
                data_list.append({'version': 'v2'})
                return self.get_paginated_response(data_list)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data_list = serializer.data
                data_list.append({'version': 'v2'})
                return self.get_paginated_response(data_list)

            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)


@method_decorator([api_recorder], name="dispatch")
class TankWeighSyncView(APIView):

    @atomic()
    def put(self, request):
        data_list = request.data
        """
        [latesttime]
        [oper] --操作者
        [matno] --物料罐号
        [matname] --物料名称
        [slow] -- 慢称值
        [shark] -- 提前量
        [adjust] -- 调整值
        [sharktime] -- 点动时间
        [fast_speed] -- 快称速度
        [slow_speed] -- 慢称速度
        [machineno] --机台号"""
        for data in data_list:
            material_name = data.get("material_name")
            tank_no = data.get("tank_no")
            material_type = "炭黑" if data.get("material_type") == 1 else "油料"
            equip_no = data.get("equip_no")
            instance = MaterialTankStatus.objects.filter(equip_no=equip_no,
                                                         tank_no=str(tank_no),
                                                         material_type=material_type)
            if data['material_type'] == 2:
                instance = instance.exclude(line_no=2)
            elif data['material_type'] == 3:
                instance = instance.filter(line_no=2)
            try:
                instance.update(
                    material_name=material_name,
                    material_no=material_name,
                    low_value=data.get("low_value", 2),
                    advance_value=data.get("advance_value", 2),
                    adjust_value=data.get("adjust_value", 2),
                    dot_time=data.get("dot_time", 2),
                    fast_speed=data.get("fast_speed", 2),
                    low_speed=data.get("low_speed", 2),
                    product_time=data.get("product_time", datetime.datetime.now()),
                    provenance=data.get("provenance")
                )
            except Exception as e:
                raise ValidationError(f"上行同步罐称量信息失败，详情{e}")

        return Response({"message": "ok"})


class FeedBack:

    @atomic()
    def feed_record(self, base_trains, pcp_obj):
        plan_trains = pcp_obj.plan_trains
        create_list = []
        equip_no = pcp_obj.equip.equip_no
        plan_classes_uid = pcp_obj.plan_classes_uid
        product_no = pcp_obj.product_batching.stage_product_batch_no
        production_factory_date = pcp_obj.work_schedule_plan.plan_schedule.day_time
        production_classes = batch_classes = pcp_obj.work_schedule_plan.classes.global_name
        batch_group = production_group = pcp_obj.work_schedule_plan.group.global_name

        for x in range(base_trains, plan_trains + 1):
            data = dict(
                trains=x,
                equip_no=equip_no,
                plan_classes_uid=plan_classes_uid,
                product_no=product_no,
                production_factory_date=production_factory_date,
                production_classes=production_classes,
                batch_classes=batch_classes,
                batch_group=batch_group,
                production_group=production_group,
                feed_uid=plan_classes_uid + str(x)
            )
            create_list.append(FeedingMaterialLog(**data))
        FeedingMaterialLog.objects.bulk_create(create_list)


@method_decorator([api_recorder], name="dispatch")
class MaterialReleaseView(FeedBack, APIView):

    def post(self, request, *args, **kwargs):
        """{'plan_no': '2021032616541329Z08',
            'feed_trains': 8,
            'equip_no': 'Z04',
            'feed_status': '正常',
            'materials': [
                {
                    'material_name': 'C-1MB-C905-03      ',
                    'plan_weight': '111',
                    'actual_weight': '111'
                },
                {
                    'material_name': 'C-FM-C905-03-E580-硫磺    ',
                    'plan_weight': '111',
                    'actual_weight': '111'
                },
            ]
            }"""
        data = request.data
        plan_classes_uid = data.get("plan_no")  # 计划编号
        equip_no = data.get("equip_no")
        feed_trains = data.get("feed_trains")  # 当前请求的进料车次
        materials = data.get("materials")  # 原材料以及称量信息，传送带只反馈胶料称量的数据
        feed_status = data.get("feed_status") + str(feed_trains)  # 进料表类型, 默认正常, 可选['处理', '强制']
        add_feed_result = 0
        if equip_no == 'Z04':  # 4号密炼机只能通过机台去查询计划号并组装数据
            pcp = ProductClassesPlan.objects.filter(equip__equip_no=equip_no, status='运行中').order_by('id').last()
        else:
            pcp = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid, status='运行中').first()
        if not pcp:
            if equip_no == 'Z04':
                send_msg_to_terminal(f'异常: 计划不存在或不是运行状态{plan_classes_uid}(联系中控)')
            return Response(f"异常: 计划不存在或不是运行状态:{plan_classes_uid}")
        plan_classes_uid = pcp.plan_classes_uid

        # 判断是否存在异常扫码记录
        switch_flag = GlobalCodeType.objects.using('mes').filter(use_flag=True, type_name='密炼扫码异常锁定开关')
        if switch_flag:
            m_ids = BatchScanLog.objects.filter(plan_classes_uid=plan_classes_uid, scan_train=feed_trains).values('bra_code').annotate(m_id=Max('id')).values_list('m_id', flat=True)
            failed_scan = BatchScanLog.objects.filter(id__in=m_ids, is_release=False)
            if failed_scan:
                failed_scan.update(aux_tag=True)
                return Response(f"异常: 该密炼车次存在未处理扫码失败记录:{plan_classes_uid[{feed_trains}]}")

        base_train = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid).aggregate(
            base_train=Max("trains"))['base_train']
        if not base_train:
            base_train = 1
        if pcp.plan_trains > base_train:
            self.feed_record(base_train, pcp)

        fml = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, trains=feed_trains).first()
        if not fml:
            if equip_no == 'Z04':
                send_msg_to_terminal(f"异常: 车次{feed_trains}不存在[联系中控]")
            return Response(f"异常: 车次{feed_trains}不存在[联系中控]")
        batching_details = ProductBatchingDetailPlan.objects.filter(plan_classes_uid=plan_classes_uid)
        if not batching_details:
            return Response(f'异常: 未找到下计划时配方[{plan_classes_uid}](联系中控)')
        if equip_no != 'Z04':
            # 先判断上辅机传过来的原材料是否与配方原材料一致，传送带只输送胶料信息。
            recipe_material_names = set(batching_details.values_list("material_name", flat=True))
            sfj_material_names = {item.get('material_name').strip() for item in materials}
            same_values = set(recipe_material_names) & set(sfj_material_names)
            if not len(same_values) == len(recipe_material_names) == len(sfj_material_names):
                # 判定原因
                if set(recipe_material_names) - set(sfj_material_names):
                    error_message = f"投料缺少:{list(set(recipe_material_names) - set(sfj_material_names))[0]}"
                else:
                    error_message = f"未知投料:{list(set(sfj_material_names) - set(recipe_material_names))[0]}"
                fml.judge_reason = error_message
                fml.failed_flag = 2
                fml.add_feed_result = 1
                fml.save()
                if equip_no == 'Z04':
                    send_msg_to_terminal(error_message)
                return Response(error_message)
        else:  # 获取4号机投料信息
            materials = list(batching_details.annotate(plan_weight=F('actual_weight')).values('material_name', 'plan_weight', 'actual_weight'))
        # 处理数据
        handle_materials = []
        # 获取对搭设置
        mixed = ProductBatchingMixed.objects.using('mes').filter(product_batching__stage_product_batch_no=pcp.product_batching.stage_product_batch_no,
                                                                 product_batching__dev_type__category_name=pcp.equip.category.category_no,
                                                                 product_batching__used_type=4, product_batching__batching_type=2,
                                                                 ).last()
        mixed_info = {} if not mixed else {mixed.f_feed_name: mixed.f_weight, mixed.s_feed_name: mixed.s_weight}
        other_material_name = ''
        for item in materials:
            material_name = item.get('material_name').strip()
            if '掺料' in material_name or '待处理料' in material_name:
                other_material_name = material_name
                continue
            if material_name not in ['细料', '硫磺']:
                # 增加对搭料
                if mixed and material_name == mixed.origin_material_name:
                    for m_name, m_weight in mixed_info.items():
                        item = {'material_name': m_name, 'plan_weight': round(m_weight, 3), 'actual_weight': round(m_weight, 3)}
                        if item not in handle_materials:
                            handle_materials.append(item)
                else:
                    plan_weight = round(Decimal(item.get("plan_weight")), 3)
                    actual_weight = round(Decimal(item.get('actual_weight')), 3)
                    item.update({'material_name': material_name, 'plan_weight': plan_weight, 'actual_weight': actual_weight})
                    handle_materials.append(item)
            # 配方生产需要细料或者硫磺(1、细料; 2、硫磺;  3、机配+人工配)
            else:
                err_msg = ''
                try:
                    res = requests.get(url=MES_URL + 'api/v1/terminal/material-details-aux/', params={"plan_classes_uid": plan_classes_uid}, timeout=10)
                except requests.ConnectionError as e:
                    err_msg = '异常: 无法连接mes[检查网络]'
                except requests.ReadTimeout as e:
                    err_msg = '异常: mes返回配方信息超时[尝试点击强制进料]'
                else:
                    if res.status_code == 500:
                        err_msg = '异常: 获取mes配方信息出现未知错误[联系国自]'
                    else:
                        if isinstance(json.loads(res.content), str):
                            err_msg = '异常: 获取mes配方信息失败[联系工艺]'
                if err_msg:
                    if equip_no == 'Z04':
                        send_msg_to_terminal(err_msg)
                    error_log.error(f'处理后进料失败[{plan_classes_uid}-{feed_trains}]: {err_msg}')
                    return Response(err_msg)
                content = json.loads(res.content)
                material_name_weight, cnt_type_details = content['material_name_weight'], content['cnt_type_details']
                xl = [i for i in material_name_weight if i['material__material_name'] in ['细料', '硫磺']]
                if not xl:  # 通用料包码：扣重请求包含料包，但配方标准中没有则表示扫过通用条码
                    continue
                else:
                    if not cnt_type_details:
                        if equip_no == 'Z04':
                            send_msg_to_terminal("异常:未找到mes配方[联系工艺]")
                        return Response("异常:未找到mes配方[联系工艺]")
                xl_details = LoadTankMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid, scan_material_type__in=['机配', '人工配'], useup_time__year='1970')
                recipe_info = [material_name] if not xl_details else [i['material__material_name'] for i in cnt_type_details]
                for i in recipe_info:
                    instance = LoadTankMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid, material_name=i).last()
                    data = {'material_name': i, 'plan_weight': 0 if not instance else instance.single_need,
                            'actual_weight': 0 if not instance else instance.single_need}
                    handle_materials.append(data)
                else:
                    continue
        # 未扫掺料或待处理料
        if other_material_name:
            scan_info = OtherMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid, other_type=other_material_name, status=1).last()
            if not scan_info:
                if equip_no == 'Z04':
                    send_msg_to_terminal(f"异常: {other_material_name}未扫码'")
                return Response(f"异常: {other_material_name}未扫码")
        error_message = ""
        success = True
        # 再判断配方的所有的物料条码是否正确
        for item in handle_materials:
            material_name = item.get('material_name')
            plan_weight = item.get("plan_weight")
            actual_weight = item.get('actual_weight')
            last_load_log = LoadMaterialLog.objects.filter(feed_log__plan_classes_uid=plan_classes_uid, status=1, material_name=material_name).order_by('id').last()
            if last_load_log:
                # 判断当前车次是否进了该物料
                m_load_log = LoadMaterialLog.objects.filter(feed_log=fml, status=1, material_name=material_name).last()
                # 判断上一车该物料剩余是够足够一车, 不够提示扫码(防止物料不足时不扫码直接使用)
                history_materials = LoadTankMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid,
                                                                                    useup_time__year='1970',
                                                                                    material_name=material_name)
                adjust_left_weight = history_materials.aggregate(left_weight=Sum('real_weight'))['left_weight']
                if not adjust_left_weight:
                    adjust_left_weight = 0
                else:
                    # 存在历史物料
                    if history_materials.last().bra_code.startswith('MC'):
                        plan_weight = history_materials.last().single_need
                        item['plan_weight'] = plan_weight
                        item.update({'plan_weight': plan_weight, 'actual_weight': plan_weight})
                if adjust_left_weight < plan_weight:
                    success = False
                    error_message += f"需扫码使用新料: {material_name}" if not error_message else f"&{material_name}"
                    add_feed_result = 1
                    break
                if not m_load_log:
                    # 当前车次未进该物料, 新建该物料的上料记录
                    LoadMaterialLog.objects.create(feed_log=fml, material_no=last_load_log.material_no,
                                                   material_name=last_load_log.material_name,
                                                   bra_code=last_load_log.bra_code,
                                                   status=last_load_log.status,
                                                   plan_weight=plan_weight,
                                                   actual_weight=actual_weight,
                                                   display_name=last_load_log.display_name,
                                                   scan_material=last_load_log.scan_material,
                                                   scan_material_type=last_load_log.scan_material_type,
                                                   stage=last_load_log.stage,
                                                   created_username=last_load_log.created_username
                                                   )
                else:
                    # 更新物料记录
                    m_load_log.plan_weight = plan_weight
                    m_load_log.actual_weight = actual_weight
                    m_load_log.save()
            else:
                # 该车次无正常进料
                success = False
                add_feed_result = 1
                error_message += f"条码信息未找到: {material_name}" if not error_message else f"&{material_name}"
        if success:
            # 修改feed_log的状态和进料时间
            time_now = datetime.datetime.now()
            fml.feed_begin_time = time_now
            fml.feed_end_time = time_now
            fml.feed_status = feed_status if not fml.feed_status else fml.feed_status + '-' + feed_status
            fml.add_feed_result = add_feed_result
            fml.created_username = self.request.user.username
            fml.save()
            # 扣重
            for item in handle_materials:
                material_name = item.get('material_name')
                actual_weight = item.get('actual_weight')
                # 该计划料框表中物料使用情况
                used_material_info = LoadTankMaterialLog.objects.using('mes').filter(useup_time__year='1970',
                                                                                     plan_classes_uid=plan_classes_uid,
                                                                                     material_name=material_name).order_by('id')
                num = used_material_info.count()
                # 该计划 物料最新使用记录
                load_tank = used_material_info.last()
                # 同物料单条未用完记录, 直接扣重
                if num == 1:
                    load_tank.actual_weight = load_tank.actual_weight + actual_weight
                    load_tank.adjust_left_weight = load_tank.adjust_left_weight - actual_weight
                    load_tank.real_weight = load_tank.real_weight - actual_weight
                    # 修正最后一车重量(单位不为包)
                    if feed_trains == pcp.plan_trains and load_tank.unit != '包':
                        # 获取实际扣重的车次
                        total_feed_trains = 0
                        feed_train_records = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, feed_end_time__isnull=False)
                        for j in feed_train_records:
                            total_feed_trains += len(j.feed_status.split('-'))
                        total_need_weight = load_tank.single_need * (feed_trains if not total_feed_trains else (total_feed_trains if total_feed_trains < feed_trains else feed_trains))
                        actual_scan_weight = load_tank.init_weight
                        load_tank.real_weight = 0 if actual_scan_weight - total_need_weight < 0 else actual_scan_weight - total_need_weight
                        load_tank.adjust_left_weight = load_tank.real_weight
                    if load_tank.real_weight == 0:
                        load_tank.useup_time = datetime.datetime.now()
                    load_tank.save()
                # 同物料多条未用完记录, 复合扣重
                else:
                    # 同名物料总重
                    material_total_weight = used_material_info.aggregate(material_total_weight=Sum('real_weight'))['material_total_weight']
                    # 除最新条码外之前条码总剩余量
                    last_material_total_weight = used_material_info[0: num - 1].aggregate(last_material_total_weight=Sum('real_weight'))['last_material_total_weight']
                    load_tank.adjust_left_weight = material_total_weight - actual_weight
                    load_tank.real_weight = material_total_weight - actual_weight
                    load_tank.actual_weight = actual_weight - last_material_total_weight
                    if load_tank.real_weight == 0:
                        load_tank.useup_time = datetime.datetime.now()
                    # 旧条码归零
                    for last_material in used_material_info[0: num - 1]:
                        last_material.adjust_left_weight = 0
                        last_material.real_weight = 0
                        last_material.actual_weight = last_material.init_weight
                        last_material.useup_time = datetime.datetime.now()
                        last_material.save()
                    load_tank.save()
            return Response('success')
        else:
            fml.judge_reason = error_message
            fml.failed_flag = 2
            fml.add_feed_result = add_feed_result
            fml.save()
            if equip_no == 'Z04':
                send_msg_to_terminal(error_message)
            return Response(error_message)


@method_decorator([api_recorder], name="dispatch")
class CurrentWeighView(FeedBack, APIView):

    def post(self, request, *args, **kwargs):
        """{"bra_code": "条形码",
            "plan_classes_uid": "计划编号",
            "material_no": "物料编码",
            "material_name": "物料名称",
            "trains": "车次",
            "status": 1,  1成功 C-1MB-C905-03  C-FM-C905-03-E580-硫磺
            "equip_no": "Z08"}"""
        data_list = request.data
        details = data_list.get('attrs')
        created_username = data_list.get('created_username')
        scan_material = data_list.get('scan_material')
        scan_material_type = data_list.get('scan_material_type')
        for data in details:
            material_status = data.get("status")  # 条码状态，正常或者异常
            bra_code = data.get("bra_code")  # 条形码
            material_no = data.get("material_no")  # 条码代表的物料编号
            material_name = data.get("material_name")  # 条码代表的物料名称
            plan_classes_uid = data.get('plan_classes_uid')
            feed_trains = data.get('trains')

            base_train = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid).aggregate(
                base_train=Max("trains"))['base_train']
            if not base_train:
                base_train = 1
            try:
                pcp = ProductClassesPlan.objects.get(plan_classes_uid=plan_classes_uid)
            except:
                raise ValidationError(f"没有{plan_classes_uid}这条计划")
            if pcp.plan_trains > base_train:
                self.feed_record(base_train, pcp)
            # 根据扫描的条码信息，记录一条数据。
            fml = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, trains=int(feed_trains)).last()
            display_name = f'{scan_material_type}({material_name}...)' if scan_material_type in ['人工配', '机配'] else material_name
            stage = pcp.product_batching.stage_product_batch_no.split('-')
            s_stage = None if not stage else (stage[1] if len(stage) > 2 else stage[0])
            LoadMaterialLog.objects.get_or_create(
                feed_log=fml,
                material_no=material_no,
                material_name=material_name,
                bra_code=bra_code,
                status=int(material_status),
                created_username=created_username,
                display_name=display_name,
                scan_material=scan_material if scan_material else display_name,
                scan_material_type=scan_material_type,
                stage=s_stage
            )
        return Response('ok')


@method_decorator([api_recorder], name="dispatch")
class ForceFeedView(APIView):

    # permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        equip_no = request.query_params.get("equip_no")
        feed_status = request.query_params.get("feed_status")
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        try:
            status, text = WebService.issue(request.query_params, 'force_feed', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            return Response({"success": False, "message": f"{equip_no} 称量反馈异常", "data": {}})
        except:
            return Response({"success": False, "message": f"{equip_no} 网络连接异常", "data": {}})
        if not status:
            return Response({"success": False, "message": f"{equip_no} 称量信息未反馈", "data": {}})
        return Response({"success": True, "message": f"{feed_status} 请求进料", "data": {}})


@method_decorator([api_recorder], name='dispatch')
class HandleFeedView(APIView):
    """物料不足扣重，扫码补料后点击验证物料"""

    def post(self, request, *args, **kwargs):
        attrs_data = self.request.data.get('attrs')
        # 存在attrs:补料自动调用; 否则为终端调用
        data = attrs_data[0] if attrs_data else self.request.data
        plan_classes_uid = data.get('plan_classes_uid')
        feed_status = data.get('handle_type', '扫码')
        equip_no = data.get("equip_no")
        trains = data.get("trains")
        pcp = ProductClassesPlan.objects.filter(plan_classes_uid=plan_classes_uid, status='运行中').first()
        if not pcp:
            return Response({"success": False, "message": f"计划不存在或不是运行状态:{plan_classes_uid}"})
        # 掺料或者待处理料未扫码
        other_material = ProductBatchingDetailPlan.objects.filter(Q(material_name__icontains='掺料') |
                                                                  Q(material_name__icontains='待处理料'),
                                                                  plan_classes_uid=plan_classes_uid).last()
        if other_material:
            scan_info = OtherMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid, status=1,
                                                                     other_type=other_material.material_name).last()
            if not scan_info:
                return Response({"success": False, "message": f"{other_material.material_name}未扫码"})
        # mes配方
        err_msg = ''
        try:
            res = requests.get(url=MES_URL + 'api/v1/terminal/material-details-aux/', params={"plan_classes_uid": plan_classes_uid}, timeout=10)
        except requests.ConnectionError as e:
            err_msg = '异常: 无法连接mes[检查网络]'
        except requests.ReadTimeout as e:
            err_msg = '异常: mes返回配方信息超时[稍后继续尝试]'
        else:
            if res.status_code == 500:
                err_msg = '异常: 获取mes配方信息出现未知错误[联系国自]'
            else:
                if isinstance(json.loads(res.content), str):
                    err_msg = '异常: 获取mes配方信息失败[联系工艺]'
        if err_msg:
            error_log.error(f'处理后进料失败[{plan_classes_uid}-{trains}]: {err_msg}')
            return Response({"success": False, "message": err_msg})
        content = json.loads(res.content)
        material_name_weight, cnt_type_details = content['material_name_weight'], content['cnt_type_details']
        xl_details = LoadTankMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid, scan_material_type__in=['机配', '人工配'], useup_time__year='1970')
        recipe_info = [i['material__material_name'] for i in material_name_weight]
        if xl_details:
            recipe_info = [i['material__material_name'] for i in material_name_weight + cnt_type_details if i['material__material_name'] not in ['硫磺', '细料']]
        # 料框表信息
        load_info = LoadTankMaterialLog.objects.using('mes').filter(plan_classes_uid=plan_classes_uid,
                                                                    useup_time__year='1970') \
            .values('material_name').annotate(total_left=Sum('real_weight'), single_need=Avg('single_need'))
        # 物料种类不对
        if set(recipe_info) != set(load_info.values_list('material_name', flat=True)):
            unknow_material = '&'.join(list(set(load_info.values_list('material_name', flat=True)) - set(recipe_info)))
            not_found_material = '&'.join(list(set(recipe_info) - set(load_info.values_list('material_name', flat=True))))
            reason = '不在配方中物料: ' + unknow_material if unknow_material else '未扫码物料: ' + not_found_material
            yk_flag, yk_msg = self.send_to_yk(equip_no, "异常", reason)
            return Response({"success": False, "message": "物料种类不一致"})
        # 剩余量仍然不足
        quantity = [i for i in load_info if i['total_left'] < i['single_need']]
        if len(quantity) != 0:
            yk_flag, yk_msg = self.send_to_yk(equip_no, "异常", '物料单重不足')
            return Response({"success": False, "message": '物料不足, 不可进料'})
        # 当前车次已经进料了, 返回false
        is_feed_end = FeedingMaterialLog.objects.filter(plan_classes_uid=plan_classes_uid, trains=trains,
                                                        feed_end_time__isnull=False)
        if is_feed_end:
            yk_flag, yk_msg = self.send_to_yk(equip_no, feed_status, '')
            return Response({"success": False, "message": f"当前车次: {trains}已完成进料"})
        yk_flag, yk_msg = self.send_to_yk(equip_no, feed_status, '')
        return Response({"success": yk_flag, "message": yk_msg})

    def send_to_yk(self, equip_no, feed_status, reason):
        # 物料种类正确且数量充足, 可以进料
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        try:
            status, text = WebService.issue({"status": feed_status, 'reason': reason}, 'force_feed', equip_no=ext_str, equip_name="上辅机")
        except APIException:
            return False, f"{equip_no} 称量反馈异常"
        except:
            return False, f"{equip_no} 网络连接异常"
        if not status:
            return False, f"{equip_no} 称量信息未反馈"
        return True, f"{feed_status} 请求进料"


@method_decorator([api_recorder], name='dispatch')
class ManualInputTrainsView(APIView):
    """手动录入车次信息"""
    permission_classes = (IsAuthenticatedOrReadOnly, )

    def get(self, request):
        query_set = ManualInputTrains.objects.using('mes').order_by('id')
        factory_date = self.request.query_params.get('factory_date')
        equip_no = self.request.query_params.get('equip_no')
        if factory_date:
            query_set = query_set.filter(factory_date=factory_date)
        if equip_no:
            query_set = query_set.filter(equip_no=equip_no)
        return Response(query_set.values())

    def post(self, request):
        data = self.request.data
        data['created_username'] = self.request.user.username
        equip_no = data['equip_no']
        product_no = data['product_no']
        pb = ProductBatching.objects.filter(batching_type=1,
                                            equip__equip_no=equip_no,
                                            stage_product_batch_no=product_no).order_by('id').last()
        if pb:
            data['weight'] = pb.batching_weight
        ManualInputTrains.objects.using('mes').create(**data)
        return Response('OK')

    def put(self, request):
        data = self.request.data
        ManualInputTrains.objects.using('mes').filter(id=data['id']).update(**data)
        return Response('OK')

    def delete(self, request):
        instance_id = self.request.data.get('id')
        ManualInputTrains.objects.using('mes').filter(id=instance_id).delete()
        return Response('OK')
