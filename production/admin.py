from django.contrib import admin

# Register your models here.
from production.models import TrainsFeedbacks,PlanStatus

admin.site.register([TrainsFeedbacks,PlanStatus])