from django.shortcuts import render

# Create your views here.
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from basics.models import GlobalCode
from datain.serializers import GlobalCodeReceiveSerializer, WorkScheduleReceiveSerializer, \
    ClassesDetailReceiveSerializer, EquipCategoryAttributeSerializer, EquipSerializer, PlanScheduleSerializer, \
    WorkSchedulePlanSerializer, MaterialSerializer, GlobalCodeTypeSerializer
from mes.derorators import api_recorder


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeReceive(CreateAPIView):
    serializer_class = GlobalCodeReceiveSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class WorkScheduleReceive(CreateAPIView):
    serializer_class = WorkScheduleReceiveSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class ClassesDetailReceive(CreateAPIView):
    serializer_class = ClassesDetailReceiveSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class EquipCategoryAttributeReceive(CreateAPIView):
    serializer_class = EquipCategoryAttributeSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class EquipReceive(CreateAPIView):
    serializer_class = EquipSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class PlanScheduleReceive(CreateAPIView):
    serializer_class = PlanScheduleSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class WorkSchedulePlanReceive(CreateAPIView):
    serializer_class = WorkSchedulePlanSerializer
    queryset = GlobalCode.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


@method_decorator([api_recorder], name="dispatch")
class MaterialReceive(CreateAPIView):
    serializer_class = MaterialSerializer
    queryset = GlobalCode.objects.all()

@method_decorator([api_recorder], name="dispatch")
class GlobalCodeTypeReceive(CreateAPIView):
    serializer_class = GlobalCodeTypeSerializer
    queryset = GlobalCode.objects.all()
