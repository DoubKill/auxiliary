import datetime
import re

import requests
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ViewSet

from basics.models import PlanSchedule
from mes.common_code import CommonDeleteMixin
from basics.models import PlanSchedule, Equip
from mes.derorators import api_recorder
from mes.paginations import SinglePageNumberPagination
from plan.models import ProductClassesPlan
from production.filters import TrainsFeedbacksFilter, PalletFeedbacksFilter, QualityControlFilter, EquipStatusFilter, \
    PlanStatusFilter, ExpendMaterialFilter, WeighParameterCarbonFilter, MaterialStatisticsFilter
from production.models import TrainsFeedbacks, PalletFeedbacks, EquipStatus, PlanStatus, ExpendMaterial, OperationLog, \
    QualityControl, MaterialTankStatus, IfupReportBasisBackups
from production.serializers import QualityControlSerializer, OperationLogSerializer, ExpendMaterialSerializer, \
    PlanStatusSerializer, EquipStatusSerializer, PalletFeedbacksSerializer, TrainsFeedbacksSerializer, \
    ProductionRecordSerializer, MaterialTankStatusSerializer, \
    WeighInformationSerializer, MixerInformationSerializer, CurveInformationSerializer, MaterialStatisticsSerializer
from production.utils import strtoint
from work_station.api import IssueWorkStation
from work_station.models import IfdownRecipeCb1, IfdownRecipeOil11
from django.db.models import Sum, Max


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
    queryset = PalletFeedbacks.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PalletFeedbacksSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = EquipStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = EquipStatusFilter

    def list(self, request, *args, **kwargs):
        actual_trains = request.query_params.get("actual_trains", '')
        if "," in actual_trains:
            train_list = actual_trains.split(",")
            try:
                queryset = self.filter_queryset(self.get_queryset().filter(current_trains__gte=train_list[0],
                                                                           current_trains__lte=train_list[-1]))
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PlanStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PlanStatusFilter


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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ExpendMaterialSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ('id',)
    filter_class = ExpendMaterialFilter


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


class PlanRealityViewSet(mixins.ListModelMixin,
                         GenericViewSet):

    def list(self, request, *args, **kwargs):
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


class ProductActualViewSet(mixins.ListModelMixin,
                           GenericViewSet):
    """密炼实绩"""

    def list(self, request, *args, **kwargs):
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

    def list_bak(self, request, *args, **kwargs):
        params = request.query_params
        day_time = params.get("search_time", str(datetime.date.today() - datetime.timedelta(days=1)))
        if day_time:
            if not re.search(r"[0-9]{4}\-[0-9]{1,2}\-[0-9]{1,2}", day_time):
                return Response("bad search_time", status=400)
        equip_no = params.get('equip_no')
        if equip_no:
            equip_no_str = f" and e.equip_no={equip_no}"
        else:
            equip_no_str = ""
        sql_str = f"""
            select pdp.id,
            pb.stage_product_batch_no as product_no,
            tf.plan_trains,
            tf.actual_trains,
            e.equip_no,
            gc.global_name,
            SUM(pcp.plan_trains) as plan_trains_all,
            sum(tf.actual_trains) as actual_trains_all,
            sum(pcp.time) as plan_time_all,
            sum(pcp.weight) as plan_weight_all,
            SUM(tf.actual_trains) as actual_weight_all,
            (sum(julianday(tf.end_time)- julianday(tf.begin_time)))*86400 as actual_time_all
            --        timediff(tf.end_time, tf.begin_time) as ac_time

            from product_day_plan as pdp
            left join plan_schedule ps on pdp.plan_schedule_id = ps.id
            left join equip e on pdp.equip_id = e.id
            left join product_classes_plan pcp on pdp.id = pcp.product_day_plan_id
            left join trains_feedbacks tf on pcp.plan_classes_uid = tf.plan_classes_uid
            left join product_batching pb on pb.id = pdp.product_batching_id
            left join work_schedule_plan wsp on pcp.work_schedule_plan_id = wsp.id
            left join global_code gc on wsp.classes_id = gc.id
            where ps.day_time = '{day_time}'{equip_no_str} 
            group by e.equip_no, gc.global_name order by e.equip_no;
        """
        query_set = TrainsFeedbacks.objects.raw(sql_str)
        return


class ProductionRecordViewSet(mixins.ListModelMixin,
                              GenericViewSet):
    queryset = PalletFeedbacks.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ProductionRecordSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = PalletFeedbacksFilter


class WeighParameterCarbonViewSet(CommonDeleteMixin, ModelViewSet):
    queryset = MaterialTankStatus.objects.filter(delete_flag=False, tank_type="1")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialTankStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = WeighParameterCarbonFilter

    # def create(self, request, *args, **kwargs):
    #     params = request.data
    #     temp_data = {
    #         # "id": 1,
    #         "mname": params.get("material_name"),
    #         "set_weight": None,
    #         "error_allow": None,
    #         "recipe_name": "配方1",
    #         "type": params.get("tank_type"),
    #         "recstatus": "None",
    #     }
    #     temp = IssueWorkStation("IfdownRecipeCb1", temp_data)
    #     temp.issue_to_db()
    #     return super().create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        data = request.data
        for i in data:
            id = i.get("id")
            # id = i['id']
            obj = MaterialTankStatus.objects.get(pk=id)
            obj.tank_name = i.get("tank_name")
            obj.material_name = i.get("material_name")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.save()
            # temp_data = {
            #     "id": id if id else None,
            #     "mname": i.get("material_name", ""),
            #     "set_weight": None,
            #     "error_allow": None,
            #     "recipe_name": "配方1",
            #     "type": i.get("tank_type"),
            #     "recstatus": "None",
            # }
            # temp = IssueWorkStation("IfdownRecipeCb1", temp_data)
            # temp.issue_to_db()
            # serializer = self.get_serializer(data=i)
            # serializer.is_valid(raise_exception=True)
            # # self.perform_create(serializer)
            #  headers = self.get_success_headers(serializer.data)
        return Response("ok", status=status.HTTP_201_CREATED)

        # return Response("ok")


class WeighParameterFuelViewSet(mixins.CreateModelMixin,
                                mixins.UpdateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                GenericViewSet):
    queryset = MaterialTankStatus.objects.filter(delete_flag=False, tank_type="2")
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialTankStatusSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = WeighParameterCarbonFilter

    def put(self, request, *args, **kwargs):
        data = request.data
        for i in data:
            id = i.get("id")
            obj = MaterialTankStatus.objects.get(pk=i.get("id"))
            obj.tank_name = i.get("tank_name")
            obj.material_name = i.get("material_name", "")
            obj.use_flag = i.get("use_flag")
            obj.low_value = i.get("low_value")
            obj.advance_value = i.get("advance_value")
            obj.adjust_value = i.get("adjust_value")
            obj.dot_time = i.get("dot_time")
            obj.fast_speed = i.get("fast_speed")
            obj.low_speed = i.get("low_speed")
            obj.save()
            # mname = i.get("material_name")
            # temp_data = {
            #     "id": id if id else None,
            #     "mname": mname if mname else "",
            #     "set_weight": None,
            #     "error_allow": None,
            #     "recipe_name": "配方1",
            #     "type": i.get("tank_type"),
            #     "recstatus": "None",
            # }
            # temp = IssueWorkStation("IfdownRecipeOil11", temp_data)
            # temp.issue_to_db()
            # serializer = self.get_serializer(data=i)
            # serializer.is_valid(raise_exception=True)
            # # self.perform_create(serializer)
            # headers = self.get_success_headers(serializer.data)
        return Response("ok", status=status.HTTP_201_CREATED)
        # ?data[]={}&data[]={}

        #     temp_data = {
        #         # "id": 1,
        #         "mname": i.get("masterial_name"),
        #         "set_weight": None,
        #         "error_allow": None,
        #         "recipe_name": "配方1",
        #         "type": i.get("tank_type"),
        #         "recstatus": None,
        #     }
        #     temp = IssueWorkStation("IfdownRecipeOil11", temp_data)
        #     temp.issue_to_db()
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)

        # return Response("ok", status=status.HTTP_201_CREATED, headers=headers)
        # return Response("ok")


class MaterialStatisticsViewSet(mixins.ListModelMixin,
                                GenericViewSet):
    queryset = ExpendMaterial.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = MaterialStatisticsSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    ordering_fields = ('id',)
    filter_class = MaterialStatisticsFilter


class EquipStatusPlanList(mixins.ListModelMixin,
                          GenericViewSet):
    """主页面展示"""

    def list(self, request, *args, **kwargs):
        air = '''SELECT equip.id,
       equip.equip_no,
       global_code.global_name,
       trains_feedbacks.product_no,
       equip_status.status,
       SUM(distinct product_classes_plan.plan_trains) AS plan_num,
       SUM(distinct trains_feedbacks.actual_trains)   AS actual_num,
       max(equip_status.current_trains)               as current_trains
from equip
         left join product_day_plan on equip.id = product_day_plan.equip_id
         left join product_classes_plan on product_day_plan.id = product_classes_plan.product_day_plan_id
         left JOIN work_schedule_plan ON (product_classes_plan.work_schedule_plan_id = work_schedule_plan.id)
         left JOIN trains_feedbacks
                   ON (trains_feedbacks.plan_classes_uid = product_classes_plan.plan_classes_uid)
         left JOIN global_code ON (work_schedule_plan.classes_id = global_code.id)
         left join equip_status on equip_status.plan_classes_uid = product_classes_plan.plan_classes_uid
where product_classes_plan.delete_flag = FALSE
  and equip_status.delete_flag = FALSE
  and trains_feedbacks.delete_flag = FALSE
GROUP BY equip.equip_no, global_code.global_name;'''
        equip_set = Equip.objects.raw(air)

        ret_data = {}
        for _ in equip_set:
            # if ret_data[_.equip_no] :
            if _.equip_no in ret_data.keys():
                ret_data[_.equip_no].append({"global_name": _.global_name,
                                             "plan_num": _.plan_num,
                                             "actual_num": _.actual_num,
                                             "product_no": _.product_no,
                                             "status": _.status,
                                             "current_trains": _.current_trains,
                                             "id": _.id})
            else:
                ret_data[_.equip_no] = []
                ret_data[_.equip_no].append({"global_name": _.global_name,
                                             "plan_num": _.plan_num,
                                             "actual_num": _.actual_num,
                                             "product_no": _.product_no,
                                             "status": _.status,
                                             "current_trains": _.current_trains,
                                             "id": _.id
                                             })

        return Response(ret_data)


class EquipDetailedList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                        GenericViewSet):
    """主页面详情展示机"""

    # queryset = Equip.objects.filter(delete_flag=False)
    # permission_classes = (IsAuthenticatedOrReadOnly,)
    # serializer_class = EquipDetailedSerializer
    # filter_backends = [DjangoFilterBackend, OrderingFilter]

    def list(self, request, *args, **kwargs):
        params = request.query_params
        equip_no = params.get('equip_no')
        air_list = f'''select equip_status.id,
       equip_status.equip_no,
       equip_status.status,
       product_batching.stage_product_batch_no as product_no,
       equip_status.current_trains,
       global_code.global_name                 as classes_name
from equip_status
         left join product_classes_plan
                   on equip_status.plan_classes_uid = product_classes_plan.plan_classes_uid
         left join product_day_plan on product_classes_plan.product_day_plan_id = product_day_plan.id
         left join product_batching on product_day_plan.product_batching_id = product_batching.id
         left join work_schedule_plan on product_classes_plan.work_schedule_plan_id = work_schedule_plan.id
         left join global_code on work_schedule_plan.classes_id = global_code.id
where equip_status.equip_no = '{equip_no}' and product_classes_plan.delete_flag=FALSE and equip_status.delete_flag=FALSE
order by equip_status.product_time desc
limit 1;'''
        try:
            equip_list = EquipStatus.objects.raw(air_list)[0]
        except Exception as e:
            # return Response('暂无数据', status=400)
            raise ValidationError('暂无数据')

        ret_data = {}
        ret_data['equip_no'] = equip_list.equip_no
        ret_data['status'] = equip_list.status
        ret_data['product_no'] = equip_list.product_no
        ret_data['current_trains'] = equip_list.current_trains
        ret_data['classes_name'] = equip_list.classes_name
        ret_data['product_list'] = []
        ret_data['status_list'] = []
        air_product_list = f'''select equip_status.id,
       product_batching.stage_product_batch_no,
       SUM(distinct product_classes_plan.plan_trains) AS plan_num,
       SUM(distinct trains_feedbacks.actual_trains)   AS actual_num
from equip_status
         left join product_classes_plan
                   on equip_status.plan_classes_uid = product_classes_plan.plan_classes_uid
         left join product_day_plan on product_classes_plan.product_day_plan_id = product_day_plan.id
         left join product_batching on product_day_plan.product_batching_id = product_batching.id
         left JOIN trains_feedbacks
                   ON trains_feedbacks.plan_classes_uid = product_classes_plan.plan_classes_uid
where equip_status.equip_no = '{equip_no}' and product_classes_plan.delete_flag = FALSE and equip_status.delete_flag=FALSE and trains_feedbacks.delete_flag = FALSE
group by product_batching.stage_product_batch_no;'''

        try:
            product_list = EquipStatus.objects.raw(air_product_list)
        except Exception as e:
            # return Response('暂无数据', status=400)
            raise ValidationError('暂无数据')
        for _ in product_list:
            p_list = {}
            p_list['product_no'] = _.stage_product_batch_no
            p_list['plan_num'] = _.plan_num
            p_list['actual_num'] = _.actual_num
            ret_data['product_list'].append(p_list)

        air_status_list = f'''select equip_status.id,
       equip_status.status,
       count(equip_status.status) as count_status
from equip_status
where equip_status.equip_no = '{equip_no}' and equip_status.delete_flag=FALSE
group by equip_status.status;
'''

        try:
            status_list = EquipStatus.objects.raw(air_status_list)
        except Exception as e:
            # return Response('暂无数据', status=400)
            raise ValidationError('暂无数据')
        for _ in status_list:
            s_list = {}
            s_list['status'] = _.status
            s_list['count_status'] = _.count_status
            ret_data['status_list'].append(s_list)
        return Response(ret_data)


class WeighInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """称量信息"""
    queryset = TrainsFeedbacks.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = SinglePageNumberPagination
    serializer_class = WeighInformationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]


class MixerInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """密炼信息"""
    queryset = TrainsFeedbacks.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = SinglePageNumberPagination
    serializer_class = MixerInformationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]


class CurveInformationList(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                           GenericViewSet):
    """工艺曲线信息"""
    queryset = TrainsFeedbacks.objects.filter(delete_flag=False)
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = SinglePageNumberPagination
    serializer_class = CurveInformationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]


class TrainsFeedbacksAPIView(mixins.ListModelMixin,
                             GenericViewSet):
    """车次报表展示接口"""
    queryset = TrainsFeedbacks.objects.all()

    def list(self, request, *args, **kwargs):
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
        tf_queryset = TrainsFeedbacks.objects.values('plan_classes_uid', 'equip_no', 'product_no').annotate(
            Max('product_time')).filter(**filter_dict).values()
        counts = tf_queryset.count()
        tf_queryset = tf_queryset[(page - 1) * page_size:page_size * page]
        # if count % page_size:
        #     counts = count // page_size + 1
        # else:
        #     counts = count // page_size
        for tf_obj in tf_queryset:
            production_details = {}
            irb_obj = IfupReportBasisBackups.objects.filter(机台号=strtoint(tf_obj['equip_no']),
                                                            计划号=tf_obj['plan_classes_uid'],
                                                            配方号=tf_obj['product_no']).order_by('存盘时间').last()
            if irb_obj:
                production_details['控制方式'] = irb_obj.控制方式  # 本远控
                production_details['作业方式'] = irb_obj.作业方式  # 手自动
                production_details['总重量'] = irb_obj.总重量
                production_details['排胶时间'] = irb_obj.排胶时间
                production_details['排胶温度'] = irb_obj.排胶温度
                production_details['排胶能量'] = irb_obj.排胶能量
                production_details['员工代号'] = irb_obj.员工代号
                production_details['存盘时间'] = irb_obj.存盘时间
                production_details['间隔时间'] = irb_obj.间隔时间
                production_details['密炼时间'] = irb_obj.存盘时间  # 暂时由存盘时间代替 后期需要确实是否是存盘时间-开始时间
                tf_obj['production_details'] = production_details
            else:
                tf_obj['production_details'] = None
            ps_obj = PlanStatus.objects.filter(equip_no=tf_obj['equip_no'], plan_classes_uid=tf_obj['plan_classes_uid'],
                                               product_no=tf_obj['product_no']).last()
            if ps_obj:
                tf_obj['status'] = ps_obj.status
            else:
                tf_obj['status'] = None

        return Response({'count': counts, 'results': tf_queryset})
