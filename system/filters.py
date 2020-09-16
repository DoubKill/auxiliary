import django_filters

from system.models import User, GroupExtension, InterfaceOperationLog


class UserFilter(django_filters.rest_framework.FilterSet):
    num = django_filters.CharFilter(field_name='num', lookup_expr='icontains', help_text='工号')
    username = django_filters.CharFilter(field_name='username', lookup_expr='icontains', help_text='用户名')
    groups = django_filters.CharFilter(field_name='groups', help_text='角色id')
    is_leave = django_filters.BooleanFilter(field_name='user_extension__is_leave', help_text='是否离职')

    class Meta:
        model = User
        fields = ('num', 'username', 'is_leave', 'groups', 'is_active')


class GroupExtensionFilter(django_filters.rest_framework.FilterSet):
    group_code = django_filters.CharFilter(field_name="group_code", lookup_expr="icontains", help_text="角色代码")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains", help_text="角色名称")

    class Meta:
        model = GroupExtension
        fields = ("group_code", "name", "use_flag")


class InterfaceOperationLogFilter(django_filters.rest_framework.FilterSet):
    username = django_filters.CharFilter(field_name="user__username", lookup_expr="icontains", help_text="用户名")
    st = django_filters.DateTimeFilter(field_name='create_time', help_text="开始时间", lookup_expr="gte")
    et = django_filters.DateTimeFilter(field_name='create_time', help_text="结束时间", lookup_expr="lte")
    operation = django_filters.CharFilter(field_name="operation", lookup_expr="icontains", help_text="操作")

    class Meta:
        model = InterfaceOperationLog
        fields = ("username", "st", "et", 'operation')
