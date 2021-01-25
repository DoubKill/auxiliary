import json

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import model_to_dict

from mes.conf import COMMON_READ_ONLY_FIELDS
from plan.models import ProductClassesPlan, ProductBatchingClassesPlan
from production.models import ExpendMaterial, MaterialTankStatus
from recipe.models import Material, ProductInfo, ProductRecipe, ProductBatching, ProductBatchingDetail, ProductProcess, \
    ProductProcessDetail, RecipeUpdateHistory
from recipe.serializers import ProductBatchingRetrieveSerializer
from system.models import DataChangeLog


def inner(sender, instance, created):
    try:
        if created:
            DataChangeLog.objects.create(
                src_table_name=sender.__name__,
                method=1,
                content=model_to_dict(instance, exclude=COMMON_READ_ONLY_FIELDS),
                user=instance.created_user
            )
        else:
            DataChangeLog.objects.create(
                src_table_name=sender.__name__,
                method=2,
                content=model_to_dict(instance, exclude=COMMON_READ_ONLY_FIELDS),
                user=instance.last_updated_user
            )
    except Exception:
        pass


@receiver(post_save, sender=Material)
def material_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)
    if not created:
        """原材料修改后更新其他两张表的数据"""
        ExpendMaterial.objects.filter(material_no=instance.material_no).update(
            material_type=instance.material_type.global_name,
            material_name=instance.material_name)
        MaterialTankStatus.objects.filter(material_name=instance.material_name).update(
            material_type=instance.material_type.global_name,
            material_name=instance.material_name)


@receiver(post_save, sender=ProductInfo)
def product_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductRecipe)
def recipe_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductBatching)
def batching_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductBatchingDetail)
def batching_detail_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductProcess)
def process_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductProcessDetail)
def process_detail_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductClassesPlan)
def plan_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


@receiver(post_save, sender=ProductBatchingClassesPlan)
def class_plan_in_post_save(sender, instance=None, created=False, update_fields=None, **kwargs):
    inner(sender, instance, created)


# @receiver(post_save, sender=ProductBatching)
def update_product_batching(sender, instance=None, created=False, **kwargs):
    try:
        if not created:
            data = ProductBatchingRetrieveSerializer(instance).data
            RecipeUpdateHistory.objects.create(
                product_no=instance.stage_product_batch_no,
                equip_no=instance.equip.equip_no,
                recipe_detail=json.loads(json.dumps(data)),
                username=instance.last_updated_user.username
            )
    except Exception:
        pass