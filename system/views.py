
import xlrd
from django.contrib.auth.models import Permission
from django.utils.decorators import method_decorator
from rest_framework import mixins, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework_jwt.views import ObtainJSONWebToken

from mes.common_code import CommonDeleteMixin
from mes.derorators import api_recorder
from mes.paginations import SinglePageNumberPagination
from plan.models import ProductClassesPlan
from recipe.models import ProductBatching
from system.models import GroupExtension, User, Section, SystemConfig, ChildSystemInfo
from system.serializers import GroupExtensionSerializer, GroupExtensionUpdateSerializer, UserSerializer, \
    UserUpdateSerializer, SectionSerializer, PermissionSerializer, GroupUserUpdateSerializer, SystemConfigSerializer, \
    ChildSystemInfoSerializer
from django_filters.rest_framework import DjangoFilterBackend
from system.filters import UserFilter, GroupExtensionFilter


@method_decorator([api_recorder], name="dispatch")
class PermissionViewSet(ReadOnlyModelViewSet):
    """
    list:
        权限列表
    create:
        创建权限
    update:
        修改权限
    destroy:
        删除权限
    """
    queryset = Permission.objects.filter()
    serializer_class = PermissionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = SinglePageNumberPagination
    # filter_backends = (DjangoFilterBackend,)


@method_decorator([api_recorder], name="dispatch")
class UserViewSet(ModelViewSet):
    """
    list:
        用户列表
    create:
        创建用户
    update:
        修改用户
    destroy:
        账号停用和启用
    """
    queryset = User.objects.filter(delete_flag=False).prefetch_related('user_permissions', 'groups')
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.filter(is_active=1).values('id', 'username')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        # 账号停用和启用
        instance = self.get_object()
        if instance.is_active:
            instance.is_active = 0
        else:
            instance.is_active = 1
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        if self.action == 'list':
            return UserSerializer
        if self.action == 'create':
            return UserSerializer
        if self.action == 'update':
            return UserUpdateSerializer
        if self.action == 'retrieve':
            return UserSerializer
        if self.action == 'partial_update':
            return UserUpdateSerializer


@method_decorator([api_recorder], name="dispatch")
class UserGroupsViewSet(mixins.ListModelMixin,
                        GenericViewSet):
    queryset = User.objects.filter(delete_flag=False).prefetch_related('user_permissions', 'groups')

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    pagination_class = SinglePageNumberPagination
    filter_class = UserFilter


@method_decorator([api_recorder], name="dispatch")
class GroupExtensionViewSet(CommonDeleteMixin, ModelViewSet):  # 本来是删除，现在改为是启用就改为禁用 是禁用就改为启用
    """
    list:
        角色列表,xxx?all=1查询所有
    create:
        创建角色
    update:
        修改角色
    destroy:
        删除角色
    """
    queryset = GroupExtension.objects.filter(delete_flag=False).prefetch_related('user_set', 'permissions')
    serializer_class = GroupExtensionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = GroupExtensionFilter

    def get_permissions(self):
        if self.request.query_params.get('all'):
            return ()
        else:
            return (IsAuthenticated(),)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if self.request.query_params.get('all'):
            data = queryset.values('id', 'name')
            return Response({'results': data})
        else:
            return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupExtensionSerializer
        if self.action == 'create':
            return GroupExtensionSerializer
        elif self.action == 'update':
            return GroupExtensionUpdateSerializer
        if self.action == 'partial_update':
            return GroupExtensionUpdateSerializer
        else:
            return GroupExtensionSerializer


@method_decorator([api_recorder], name="dispatch")
class GroupAddUserViewSet(UpdateAPIView):
    """控制角色中用户具体为哪些的视图"""
    queryset = GroupExtension.objects.filter(delete_flag=False).prefetch_related('user_set', 'permissions')
    serializer_class = GroupUserUpdateSerializer


@method_decorator([api_recorder], name="dispatch")
class SectionViewSet(CommonDeleteMixin, ModelViewSet):
    """
    list:
        角色列表
    create:
        创建角色
    update:
        修改角色
    destroy:
        删除角色
    """
    queryset = Section.objects.filter(delete_flag=False)
    serializer_class = SectionSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)


class ImportExcel(APIView):

    def post(self, request, *args, **kwargs):
        excel_file = request.FILES.get('excel_file', '')
        if excel_file.name.endswith(".xlsx"):
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read())  # xlsx文件
        elif excel_file.endswith(".xls"):
            data = xlrd.open_workbook(filename=None, file_contents=excel_file.read(), formatting_info=True)  # xls
        else:
            raise TypeError
        all_list_1 = self.get_sheets_mg(data)
        for x in all_list_1:
            print(x)
        return Response({"msg": "ok"})

    def get_sheets_mg(self, data, num=0):  # data:Excel数据对象，num要读取的表
        table = data.sheets()[num]  # 打开第一张表
        nrows = table.nrows  # 获取表的行数
        ncole = table.ncols  # 获取列数
        all_list = []
        for i in range(nrows):  # 循环逐行打印
            one_list = []
            for j in range(ncole):
                cell_value = table.row_values(i)[j]
                if (cell_value is None or cell_value == ''):
                    cell_value = (self.get_merged_cells_value(table, i, j))
                one_list.append(cell_value)
            all_list.append(one_list)
        del (all_list[0])  # 删除标题   如果Excel文件中第一行是标题可删除掉，如果没有就不需要这行代码
        return all_list

    def get_merged_cells_value(self, sheet, row_index, col_index):
        """
        先判断给定的单元格，是否属于合并单元格；
        如果是合并单元格，就返回合并单元格的内容
        :return:
        """
        merged = self.get_merged_cells(sheet)
        # print(merged,"==hebing==")
        for (rlow, rhigh, clow, chigh) in merged:
            if (row_index >= rlow and row_index < rhigh):
                if (col_index >= clow and col_index < chigh):
                    cell_value = sheet.cell_value(rlow, clow)
                    # print('该单元格[%d,%d]属于合并单元格，值为[%s]' % (row_index, col_index, cell_value))
                    return cell_value
                    break
        return None

    def get_merged_cells(self, sheet):
        """
        获取所有的合并单元格，格式如下：
        [(4, 5, 2, 4), (5, 6, 2, 4), (1, 4, 3, 4)]
        (4, 5, 2, 4) 的含义为：行 从下标4开始，到下标5（不包含）  列 从下标2开始，到下标4（不包含），为合并单元格
        :param sheet:
        :return:
        """
        return sheet.merged_cells


class SystemConfigViewSet(CommonDeleteMixin, ModelViewSet):
    """
        list:
            系统配置列表
        create:
            创建系统配置
        update:
            修改系统配置
        destroy:
            删除系统配置
    """
    queryset = SystemConfig.objects.filter(delete_flag=False)
    serializer_class = SystemConfigSerializer
    permission_classes = (IsAdminUser,)


class ChildSystemInfoViewSet(CommonDeleteMixin, ModelViewSet):
    """
        list:
            子系统信息列表
        create:
            创建子系统信息
        update:
            修改子系统信息
        destroy:
            删除子系统信息
    """
    queryset = ChildSystemInfo.objects.filter(delete_flag=False)
    serializer_class = ChildSystemInfoSerializer
    pagination_class = SinglePageNumberPagination
    permission_classes = (IsAdminUser,)
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ("system_type",)


class LoginView(ObtainJSONWebToken):
    """
    post
        获取权限列表
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            # 获取该用户所有权限
            permissions = list(user.get_all_permissions())
            # 除去前端不涉及模块
            permission_list = []
            for p in permissions:
                if p.split(".")[0] not in ["contenttypes", "sessions", "work_station", "admin"]:
                    permission_list.append(p)
            # 生成菜单管理树
            permissions_set = set([_.split(".")[0] for _ in permission_list])
            permissions_tree = {__: {} for __ in permissions_set}
            for x in permission_list:
                first_key = x.split(".")[0]
                second_key = x.split(".")[-1].split("_")[-1]
                op_value = x.split(".")[-1].split("_")[0]
                op_list = permissions_tree.get(first_key, {}).get(second_key)
                if op_list:
                    permissions_tree[first_key][second_key].append(op_value)
                else:
                    permissions_tree[first_key][second_key] = [op_value]
            if permissions_tree.get("auth"):
                auth = permissions_tree.pop("auth")
                # 合并auth与system
                if permissions_tree.get("system"):
                    permissions_tree["system"].update(**auth)
                else:
                    permissions_tree["system"] = auth
            if permissions_tree.get("recipe", {}).get("material"):
                # 当有配方原材料的时候需要往生产里迁移映射关系
                if not permissions_tree.get("production"):
                    permissions_tree["production"] = {}
                material = permissions_tree["recipe"].pop("material")
                permissions_tree["production"].update(material=material)
            return Response({"results": permissions_tree,
                             "username": user.username,
                             "token": token})
        # 返回异常信息
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import datetime


class SystemStatusSwitch(APIView):
    # post: 切换系统运行状态的接口
    query_set = ChildSystemInfo.objects.filter(delete_flag=False)

    def post(self, request, *args, **kwargs):
        params = request.data
        status = params.get("system_status")
        if status not in ["联网", "独立"]:
            raise ValidationError("系统运行状态只有联网/独立")
        config = SystemConfig.objects.filter(config_name="system_name").first()
        if not config:
            raise ValidationError("系统配置异常，请联系管理员检查处理")
        config_value = config.config_value
        child_system = ChildSystemInfo.objects.filter(system_name=config_value).first()
        if not child_system:
            raise ValidationError("系统配置异常，请联系管理员检查处理")
        if child_system.status_lock:
            raise ValidationError("系统运行状态处于同步中，请稍后再试")
        child_system.status = status
        if status == '独立':
            child_system.lost_time = datetime.datetime.now()
        elif status == '联网':
            child_system.lost_time = None
        child_system.save()
        return Response("ok")


from django.db.models import Q


class Synchronization(APIView):
    """mes和上辅机同步接口"""

    def get(self, request, *args, **kwargs):
        auxliary_dict = {'lost_time': None, }  # 上辅机
        # 获取断网时间
        csi_obj = ChildSystemInfo.objects.filter(status='独立').order_by('created_date').last()
        if csi_obj:
            lost_time = csi_obj.lost_time
            auxliary_dict['lost_time'] = lost_time
            # 胶料诶班次计划表
            pcp_set = ProductClassesPlan.objects.filter(last_updated_date__gte=lost_time)
            if pcp_set:
                auxliary_dict['ProductClassesPlan'] = []
                for pcp_obj in pcp_set:
                    pcp_dict = pcp_obj.__dict__
                    pcp_dict.pop('_state')
                    auxliary_dict['ProductClassesPlan'].append(pcp_dict)
            # 胶料配料标准表
            pb_set = ProductBatching.objects.filter(last_updated_date__gte=lost_time)
            if pb_set:
                auxliary_dict['ProductBatching'] = []
                for pb_obj in pb_set:
                    pb_dict = pb_obj.__dict__
                    pb_dict.pop('_state')
                    auxliary_dict['ProductBatching'].append(pb_dict)
        return Response({'上辅机群控系统': auxliary_dict}, status=200)
