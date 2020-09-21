import logging
import re

import requests
from rest_framework import status, mixins
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.reverse import reverse

from mes.permissions import PermissonsDispatch
from system.models import User, ChildSystemInfo

logger = logging.getLogger(__name__)


class CommonDeleteMixin(object):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.use_flag:
            instance.use_flag = 0
        else:
            instance.use_flag = 1
        instance.last_updated_user = request.user
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SyncCreateMixin(mixins.CreateModelMixin):
    # 创建时需记录同步数据的接口请继承该创建插件
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        setattr(response, "model_name", self.queryset.model.__name__)
        return response


class SyncUpdateMixin(mixins.UpdateModelMixin):
    # 更新时需记录同步数据的接口请继承该更新插件
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        setattr(response, "model_name", self.queryset.model.__name__)
        return response


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


class WebService(object):
    client = requests.request
    url = "http://{}:9000/planService"

    @classmethod
    def issue(cls, data, category, method="post"):
        headers = {
            'Content-Type': 'text/xml; charset=utf-8',
            'SOAPAction': 'http://tempuri.org/INXWebService/{}'
        }

        child_system = ChildSystemInfo.objects.filter(system_name="收皮终端").first()
        recv_ip = child_system.link_address
        url = cls.url.format(recv_ip)
        headers['SOAPAction'] = headers['SOAPAction'].format(category)
        rep = cls.client(method, url, headers=headers, data=cls.trans_dict_to_xml(data, category), timeout=3)
        print(rep.text)
        if rep.status_code < 300:
            return True, rep.text
        elif rep.status_code == 500:
            logger.error(rep.text)
            return False, rep.text
        else:
            return False, rep.text

    # dict数据转soap需求xml
    @staticmethod
    def trans_dict_to_xml(data, category):
        """
        将 dict 对象转换成微信支付交互所需的 XML 格式数据

        :param data: dict 对象
        :return: xml 格式数据
        """

        xml = []
        for k in data.keys():
            v = data.get(k)
            if k == 'detail' and not v.startswith('<![CDATA['):
                v = '<![CDATA[{}]]>'.format(v)
            xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
        res = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"> <s:Body>
                    <{} xmlns="http://tempuri.org/">
                       {}
                    </{}>
                </s:Body>
                </s:Envelope>""".format(category, ''.join(xml), category)
        res = res.encode("utf-8")
        return res


def common_validator(**kwargs):
    # 通用校验器，用于校验外部入参
    for k,v in kwargs.items():
        if not re.search(r"^[a-zA-Z0-9\u4e00-\u9fa5\-\s:.]{2,19}$", v):
            raise ValidationError(f"字段{k}的值{v}非规范输入，请规范后重试")