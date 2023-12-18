# -*- coding: UTF-8 -*-
"""
auther: 
datetime: 2020/7/27
name: 
"""

COMMON_READ_ONLY_FIELDS = ('created_date', 'last_updated_date', 'delete_date',
                           'delete_flag', 'created_user', 'last_updated_user',
                           'delete_user')

PROJECT_API_TREE = {
    "basic": (),
    "system": (),
    "repice": (),
    "plan": (),
    "production": ('trains-feedbacks', 'pallet-feedbacks'),
}

SYSTEM_NAME = "上辅机群控"

SYNC_SYSTEM_NAME = "MES"

MES_PORT = "80"

EQUIP_LIST = ['Z01', 'Z02', 'Z03', 'Z04', 'Z05', 'Z06', 'Z07', 'Z08', 'Z09', 'Z10', 'Z11', 'Z12', 'Z13', 'Z14', 'Z15']

BZ_USR = "GZ_MES"

BZ_PASSWORD = "mes@_123"

BZ_HOST = "10.4.23.101"

# BZ_USR = "sa"
# BZ_PASSWORD = "123"
# BZ_HOST = "10.4.14.101"
VERSION_EQUIP = {'Z01': 'v2',
                 'Z02': 'v2', 'Z03': 'v2', 'Z04': 'v2', 'Z05': 'v2', 'Z06': 'v2', 'Z07': 'v2', 'Z08': 'v2', 'Z09': 'v2',
                 'Z10': 'v2', 'Z11': 'v2', 'Z12': 'v2', 'Z13': 'v2', 'Z14': 'v2', 'Z15': 'v2'}

hf_db = "H-Z04"

protocol="http"