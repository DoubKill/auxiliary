import django_filters

from recipe.models import Material, ProductInfo, ProductBatching, MaterialAttribute, ProductProcess


class MaterialFilter(django_filters.rest_framework.FilterSet):
    material_type_id = django_filters.NumberFilter(field_name='material_type', help_text='原材料类别')
    used_flag = django_filters.BooleanFilter(field_name='used_flag', help_text='是否使用')
    material_no = django_filters.CharFilter(field_name='material_no', help_text='原材料代码', lookup_expr='icontains')
    material_name = django_filters.CharFilter(field_name='material_name', help_text='原材料名称', lookup_expr='icontains')

    class Meta:
        model = Material
        fields = ('material_type_id', 'used_flag', 'material_no', 'material_name')


class ProductInfoFilter(django_filters.rest_framework.FilterSet):
    product_no = django_filters.CharFilter(field_name='product_no', help_text='胶料编码', lookup_expr='icontains')
    product_name = django_filters.CharFilter(field_name='product_name', help_text='胶料名称', lookup_expr='icontains')

    class Meta:
        model = ProductInfo
        fields = ('product_no', 'product_name')


class ProductBatchingFilter(django_filters.rest_framework.FilterSet):
    factory_id = django_filters.NumberFilter(field_name='product_info__factory_id', help_text='产地id')
    stage_product_batch_no = django_filters.CharFilter(field_name='stage_product_batch_no', lookup_expr='icontains',
                                                       help_text='胶料编码')
    dev_type = django_filters.NumberFilter(field_name='dev_type_id', help_text='炼胶机类型id')
    site = django_filters.NumberFilter(field_name='site', help_text='SITE')
    used_type = django_filters.NumberFilter(field_name='used_type', help_text='状态')
    stage_id = django_filters.NumberFilter(field_name='stage_id', help_text='段次id')

    class Meta:
        model = ProductBatching
        fields = ('factory_id', 'stage_id', 'stage_product_batch_no', 'dev_type', 'site', 'used_type')


class MaterialAttributeFilter(django_filters.rest_framework.FilterSet):
    material_no = django_filters.NumberFilter(field_name='material__material_no', help_text='原材料编码')

    class Meta:
        model = MaterialAttribute
        fields = ('material_no',)


class ProcessStepsFilter(django_filters.rest_framework.FilterSet):
    equip = django_filters.NumberFilter(field_name='equip', help_text='设备id')
    product_batching = django_filters.NumberFilter(field_name='product_batching', help_text='配料id')

    class Meta:
        model = ProductProcess
        fields = ('equip', 'product_batching')