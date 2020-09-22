import json
import time
import logging
import traceback

from django.http.response import HttpResponseNotFound

from system.models import InterfaceOperationLog

api_log = logging.getLogger('api_log')
error_log = logging.getLogger('error_log')


path_dict = {
    '/api/v1/recipe/materials/': '原材料',
    '/api/v1/recipe/product-infos/': '胶料代码',
    '/api/v1/recipe/product-batching/': '配方',
    '/api/v1/plan/up-regulation/': '下调计划',
    '/api/v1/plan/down-regulation/': '上调计划',
    '/api/v1/plan/update-trains/': '修改车次',
    '/api/v1/plan/issued-plan/': '计划下达',
    '/api/v1/plan/stop-plan/': '计划停止',
    '/api/v1/plan/product-day-plan-manycreate/': '计划',
    '/api/v1/system/personnels/': '用户',
    '/api/v1/system/group_extension/': '角色',
    '/api/v1/production/weigh-cb': '炭黑称量',
    '/api/v1/production/weigh-oil': '油料称量'
}

method_dict = {
    'POST': '新增：',
    'PUT': '修改：',
    'PATCH': '修改：',
    'DELETE': '弃用/启用：'
}


def api_recorder(func):
    def inner(request, *args, **kwargs):
        if 'pk' in kwargs:
            try:
                pk = int(kwargs.get('pk'))
                if not (0 < pk <= (1 << 32)):
                    return HttpResponseNotFound(content="非法资源")
            except Exception as e:
                error_log.error(e)
                return HttpResponseNotFound(content="非法资源")

        value = {
            'path': request.get_full_path(),
        }
        try:
            value.update(post=request.POST.dict())
            value.update(get=request.GET.dict())
            if request.content_type == 'application/json':
                value.update(body=json.loads(request.body))
        except Exception as e:
            error_log.error(e)
        start = time.time()

        log_instance = None
        try:
            method = request.method
            path = request.path_info
            if not path.endswith('/'):
                path += '/'
            if 'pk' in kwargs:
                path = '/'.join(path.split('/')[:-2]) + '/'
            if method in method_dict and path in path_dict:
                log_instance = InterfaceOperationLog.objects.create(
                        method=method,
                        content=json.dumps(value, ensure_ascii=False),
                        url=path,
                        operation=method_dict[method] + path_dict[path]
                    )
        except Exception:
            error_log.error(traceback.format_exc())

        try:
            resp = func(request, *args, **kwargs)
            return resp
        except Exception:
            error_log.error(traceback.format_exc())
            if log_instance:
                log_instance.results = 0
                log_instance.reasons = traceback.format_exc()
                log_instance.save()
            raise
        finally:
            finish = time.time()
            value = json.dumps(value, ensure_ascii=False)
            api_log.info(','.join(('SEND', 'http', '[%s,%s,%s,%s,%s]' % (request.method, request.user,
                                                                         request.path, round(finish - start, 3),
                                                                         value))))
            if log_instance:
                log_instance.user = request.user if request.user else None
                log_instance.save()
    return inner
