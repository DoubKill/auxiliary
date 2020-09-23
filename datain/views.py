from django.utils.decorators import method_decorator
from rest_framework.generics import CreateAPIView

from basics.models import GlobalCode
from datain.serializers import GlobalCodeReceiveSerializer, WorkScheduleReceiveSerializer, \
    ClassesDetailReceiveSerializer, EquipCategoryAttributeSerializer, EquipSerializer, PlanScheduleSerializer, \
    WorkSchedulePlanSerializer, MaterialSerializer, GlobalCodeTypeSerializer, ProductInfoSerializer, \
    RecipeReceiveSerializer
from mes.derorators import api_recorder
from recipe.models import ProductInfo, ProductBatching


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeReceive(CreateAPIView):
    serializer_class = GlobalCodeReceiveSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class WorkScheduleReceive(CreateAPIView):
    serializer_class = WorkScheduleReceiveSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class ClassesDetailReceive(CreateAPIView):
    serializer_class = ClassesDetailReceiveSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class EquipCategoryAttributeReceive(CreateAPIView):
    serializer_class = EquipCategoryAttributeSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class EquipReceive(CreateAPIView):
    serializer_class = EquipSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class PlanScheduleReceive(CreateAPIView):
    serializer_class = PlanScheduleSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class WorkSchedulePlanReceive(CreateAPIView):
    serializer_class = WorkSchedulePlanSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class MaterialReceive(CreateAPIView):
    serializer_class = MaterialSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class GlobalCodeTypeReceive(CreateAPIView):
    serializer_class = GlobalCodeTypeSerializer
    queryset = GlobalCode.objects.all()


@method_decorator([api_recorder], name="dispatch")
class ProductInfoReceive(CreateAPIView):
    serializer_class = ProductInfoSerializer
    queryset = ProductInfo.objects.all()


@method_decorator([api_recorder], name="dispatch")
class RecipeReceiveAPiView(CreateAPIView):
    """
    接受上辅机配方数据接口
    """
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RecipeReceiveSerializer
    queryset = ProductBatching.objects.all()