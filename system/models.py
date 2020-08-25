from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """用户拓展信息"""
    num = models.CharField(max_length=20, help_text='工号', verbose_name='工号', unique=True)
    is_leave = models.BooleanField(help_text='是否离职', verbose_name='是否离职', default=False)
    section = models.ForeignKey("Section", blank=True, null=True, help_text='部门', verbose_name='部门',
                                on_delete=models.DO_NOTHING)
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    delete_date = models.DateTimeField(blank=True, null=True,
                                       help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)
    created_user = models.ForeignKey('self', blank=True, null=True, related_name='c_%(app_label)s_%(class)s_related',
                                     help_text='创建人', verbose_name='创建人', on_delete=models.DO_NOTHING,
                                     related_query_name='c_%(app_label)s_%(class)ss')
    last_updated_user = models.ForeignKey('self', blank=True, null=True,
                                          related_name='u_%(app_label)s_%(class)s_related',
                                          help_text='更新人', verbose_name='更新人', on_delete=models.DO_NOTHING,
                                          related_query_name='u_%(app_label)s_%(class)ss')
    delete_user = models.ForeignKey('self', blank=True, null=True, related_name='d_%(app_label)s_%(class)s_related',
                                    help_text='删除人', verbose_name='删除人', on_delete=models.DO_NOTHING,
                                    related_query_name='d_%(app_label)s_%(class)ss')

    def __str__(self):
        return "{}".format(self.username)

    class Meta:
        db_table = "user"
        verbose_name_plural = verbose_name = '用户'
        permissions = ()


class AbstractEntity(models.Model):
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    delete_date = models.DateTimeField(blank=True, null=True,
                                       help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)
    created_user = models.ForeignKey(User, blank=True, null=True, related_name='c_%(app_label)s_%(class)s_related',
                                     help_text='创建人', verbose_name='创建人', on_delete=models.DO_NOTHING,
                                     related_query_name='c_%(app_label)s_%(class)ss')
    last_updated_user = models.ForeignKey(User, blank=True, null=True, related_name='u_%(app_label)s_%(class)s_related',
                                          help_text='更新人', verbose_name='更新人', on_delete=models.DO_NOTHING,
                                          related_query_name='u_%(app_label)s_%(class)ss')
    delete_user = models.ForeignKey(User, blank=True, null=True, related_name='d_%(app_label)s_%(class)s_related',
                                    help_text='删除人', verbose_name='删除人', on_delete=models.DO_NOTHING,
                                    related_query_name='d_%(app_label)s_%(class)ss')

    class Meta(object):
        abstract = True


class Section(AbstractEntity):
    """部门表"""
    section_id = models.CharField(max_length=40, help_text='部门ID', verbose_name='部门ID')
    name = models.CharField(max_length=30, help_text='部门名称', verbose_name='部门名称')
    description = models.CharField(max_length=256, blank=True, null=True,
                                   help_text='说明', verbose_name='说明')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'section'
        verbose_name_plural = verbose_name = '部门'


class GroupExtension(Group):
    """组织拓展信息表"""
    group_code = models.CharField(max_length=50, help_text='角色代码', verbose_name='角色代码', unique=True)
    use_flag = models.BooleanField(help_text='是否使用', verbose_name='是否使用')
    created_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    last_updated_date = models.DateTimeField(verbose_name='修改时间', auto_now=True)
    delete_date = models.DateTimeField(blank=True, null=True,
                                       help_text='删除日期', verbose_name='删除日期')
    delete_flag = models.BooleanField(help_text='是否删除', verbose_name='是否删除', default=False)
    created_user = models.ForeignKey(User, blank=True, null=True, related_name='c_%(app_label)s_%(class)s_related',
                                     help_text='创建人', verbose_name='创建人', on_delete=models.DO_NOTHING,
                                     related_query_name='c_%(app_label)s_%(class)ss')
    last_updated_user = models.ForeignKey(User, blank=True, null=True, related_name='u_%(app_label)s_%(class)s_related',
                                          help_text='更新人', verbose_name='更新人', on_delete=models.DO_NOTHING,
                                          related_query_name='u_%(app_label)s_%(class)ss')
    delete_user = models.ForeignKey(User, blank=True, null=True, related_name='d_%(app_label)s_%(class)s_related',
                                    help_text='删除人', verbose_name='删除人', on_delete=models.DO_NOTHING,
                                    related_query_name='d_%(app_label)s_%(class)ss')

    def __str__(self):
        return "{}".format(self.name)

    class Meta:
        db_table = 'group_extension'
        verbose_name_plural = verbose_name = '组织拓展信息'


class ChildSystemInfo(AbstractEntity):
    path = models.CharField(max_length=64, help_text='连接地址', verbose_name='连接地址')
    system_type = models.CharField(max_length=64, help_text='系统类型', verbose_name='系统地址')
    system_name = models.CharField(max_length=64, help_text='系统名称', verbose_name='系统名称')
    status = models.CharField(max_length=64, help_text='子系统状态', verbose_name='子系统状态')
    status_lock = models.BooleanField()

    def __str__(self):
        return f"{self.system_type}|{self.system_name}|{self.path}"

    class Meta:
        db_table = 'child_system_info'
        verbose_name_plural = verbose_name = '子系统信息'


class SystemConfig(AbstractEntity):
    category = models.CharField(max_length=64, help_text='种类', verbose_name='种类')
    config_name = models.CharField(max_length=64, help_text='配置名称', verbose_name='配置名称')
    config_value = models.CharField(max_length=64, help_text='配置值', verbose_name='配置值')
    description = models.CharField(max_length=64, help_text='描述', verbose_name='描述')

    def __str__(self):
        return f"{self.category}|{self.config_name}|{self.config_value}"

    class Meta:
        db_table = 'system_config'
        verbose_name_plural = verbose_name = '系统配置表'
