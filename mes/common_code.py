from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse

from basics.models import PlanSchedule
from mes.permissions import PermissonsDispatch
from plan.models import ProductClassesPlan
from system.models import User


class CommonDeleteMixin(object):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete_flag = True
        instance.delete_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


def return_permission_params(model_name):
    """
    :param model_name: 模型类名.lower()
    :return: permission_required需求参数
    """
    return {
        'view': f'view_{model_name}',
        'add': f'add_{model_name}',
        'delete': f'delete_{model_name}',
        'change': f'change_{model_name}'
    }


def menu(request, menu, temp, format):
    """
    生成菜单树
    :param request: http_request
    :param menu: 当前项目的菜单结构，后期动态菜单可维护到数据库
    :param temp: 继承于原函数的中间返回体
    :param format: reverse需要参数
    :return:
    """

    username = request.data.get("username")
    user = User.objects.filter(username=username).first()
    permissions = PermissonsDispatch(user)(dispatch="module")
    data = {}
    for _ in permissions:
        module, permission = _.split(".")
        m = None
        if permission.startswith("view"):
            m = permission.split("_")[1]
        module_list = menu.get(module, {})
        if m in module_list:
            if isinstance(data.get(module), dict):
                data[module].update({m: reverse(f'{m}-list', request=request, format=format)})
            else:
                data[module] = {m: reverse(f'{m}-list', request=request, format=format)}

    temp.data.update({"menu": data})
    return temp


def get_day_plan_class_set(time_str):
    plan_schedule = PlanSchedule.objects.filter(day_time=time_str).first()
    day_plan_id_list = plan_schedule.ps_day_plan.filter(delete_flag=False).values_list("id", flat=True)
    day_class_plan_set = ProductClassesPlan.objects.filter(product_day_plan__in=day_plan_id_list)
    return day_class_plan_set

def get_day_plan_class_uid_list(time_str):
    plan_schedule = PlanSchedule.objects.filter(day_time=time_str).first()
    day_plan_id_list = plan_schedule.ps_day_plan.filter(delete_flag=False).values_list("id", flat=True)
    day_class_plan_uid_list = ProductClassesPlan.objects.filter(product_day_plan__in=day_plan_id_list).values_list("plan_classes_uid", flat=True)
    return day_class_plan_uid_list