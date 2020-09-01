import json

from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from jwt import DecodeError
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework_jwt.utils import jwt_decode_handler

from mes.conf import PROJECT_API_TREE, SYNC_SYSTEM_NAME
from production.utils import OpreationLogRecorder
from system.models import SystemConfig, ChildSystemInfo, AsyncUpdateContent


class DisableCSRF(MiddlewareMixin):
    @staticmethod
    def process_request(request):
        setattr(request, '_dont_enforce_csrf_checks', True)


class OperationLogRecordMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwargs):
        method = request.method
        try:
            if method.lower() in ["put", "post", "delete", "patch"]:
                module = request.path.split("/")[3]
                api = request.path.split("/")[4]
                if module in PROJECT_API_TREE:
                    if api in PROJECT_API_TREE[module]:
                        body = request.POST.dict()
                        params = request.GET.dict()
                        content = {}
                        content.update(url=request.get_full_path(), method=method, body=body, params=params,
                                       user=request.user.username)
                        equip_no = body.get("equip_no")
                        OpreationLogRecorder(equip_no=equip_no, content=content).log_recoder()
        except Exception as e:
            pass


class SyncMiddleware(MiddlewareMixin):
    """处理异步方式进行同步接口的请求"""

    # 获取当前系统状态
    @property
    def if_system_online(self):
        system_config = SystemConfig.objects.filter(config_name="system_name").first()
        if system_config:
            config_value = system_config.config_value
        else:
            return False
        child_system = ChildSystemInfo.objects.filter(system_name=config_value).first()
        if child_system:
            self.system_name = config_value
            # 必须为联网状态切改状态在当前不可更改
            if child_system.status == "联网" and child_system.status_lock:
                return True
            return False
        return False

    def process_request(self, request):
        tag = request.META.get("HTTP_TAG")
        # 根据url判断是否为基础数据同步
        if tag:
            # 若为基础数据同步需判断是否联网
            if not self.if_system_online:
                return HttpResponse(f"系统处于非联网/独立状态，请检查系统联网配置后重试", status=400)

    def process_response(self, request, response):
        model_name = getattr(response, "model_name", None)
        if model_name:
            child_system = ChildSystemInfo.objects.filter(system_name=SYNC_SYSTEM_NAME).first()
            if child_system:
                link_address = child_system.link_address
                url = request.get_full_path()
                method = request.method
                dst_address = f"https://{link_address}{url}"
                content = json.dumps(request.POST.dict())
                AsyncUpdateContent.objects.create(content=content, method=method, src_table_name=model_name,
                                                  dst_address=dst_address)

        return response


class JwtTokenUserMiddleware(MiddlewareMixin):
    # 根据jwt-token获取user并放入request中

    def process_request(self, request):
        jwt_token = request.META.get("HTTP_AUTHORIZATION", " ")
        token = jwt_token.split(" ")[1]
        token_dict = {"token": token}
        try:
            toke_user = jwt_decode_handler(token)  # 获取用户基本数据
        except DecodeError:
            user = AnonymousUser()  # token为空或者存在编码为空则为异常访问，默认成匿名用户
        else:
            token_dict.update(username=toke_user.get("username"))  # 拼接下方序列化器所需入参
            # 校验token并获取用户对象塞入request中
            jwt_serializer = VerifyJSONWebTokenSerializer(token)
            # 获得user_id
            data = jwt_serializer.validate(token_dict)
            user = data.get("user")
            setattr(request, "user", user)