import os

import django



os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()
from recipe.models import ProductBatchingDetail
from system.models import DataSynchronization


if __name__ == '__main__':
    id_list = ProductBatchingDetail.objects.filter(product_batching__used_type=6).values_list("id", flat=True)
    # print(len(id_list))
    for d in id_list:
        DataSynchronization.objects.create(type=12, obj_id=d)