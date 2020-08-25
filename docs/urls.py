from django.urls import include, path

from mes.urls import schema_view
from system.views import ImportExcel

urlpatterns = [
    path('^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('import-excel', ImportExcel.as_view()),
]
