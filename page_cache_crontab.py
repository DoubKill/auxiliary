import os
import django
import requests

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mes.settings")
django.setup()

if __name__ == '__main__':
    requests.get("http://127.0.0.1:8000/api/v1/production/equip-status-plan-list/")