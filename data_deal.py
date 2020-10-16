# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/10/15
name: 
"""
import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

from recipe.models import Material
from basics.models import GlobalCode

def run():
    m_set = Material.objects.all()
    for m in m_set:
        try:
            temp = m.material_name.split("-")
        except:
            continue
        else:
            try:
                stage = temp[1]
                gc = GlobalCode.objects.filter(global_name=stage, global_type__type_name='原材料类别').first()
                if gc:
                    m.material_type_id = gc.id
                    m.save()
            except:
                pass

if __name__ == '__main__':
    run()