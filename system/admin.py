from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Permission
# Register your models here.
from system.models import Section, User, GroupExtension, ChildSystemInfo

admin.site.register(User, UserAdmin)
admin.site.register([Section, GroupExtension, ChildSystemInfo])
admin.site.register([Permission])
