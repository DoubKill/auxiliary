from django.db import models

# Create your models here.
from rest_framework.views import APIView


class OutWork(APIView):

    def id_create(self):
        return 123

    # 出库
    def post(self, request):
        """WMS->MES:任务编号、物料信息ID、物料名称、PDM号（促进剂以外为空）、批号、条码、重量、重量单位、
        生产日期、使用期限、托盘RFID、工位（出库口）、MES->WMS:信息接收成功or失败"""
        #任务编号
        task_id = self.id_create()
        #物料信息ID
        material_id = "a01"
        #物料名称
        material_name = "cb1"

        pass

class OutWorkFeedBack(APIView):


    # 出库反馈
    def post(self, request):
        """WMS->MES:任务编号、物料信息ID、物料名称、PDM号（促进剂以外为空）、批号、条码、重量、重量单位、
        生产日期、使用期限、托盘RFID、工位（出库口）、MES->WMS:信息接收成功or失败"""
        #任务编号
        data = request.data
        """{         
            "datas":[{
                "task_id": "123",
                "material_no": "a002",
                "pdm_no": "123",  促进剂以外为空
                "batch_no": "1",
                "lot_no": "fffffff",
                "weight": 100.00,
                "unit": "kg",
                "product_time": "2020-10-28 14:39:17",
                "expire_time": "2021-10-28 14:39:17",
                "rfid": "20120741",
                "station": "出货口1",
                "out_user": "user1",
                "out_type": "生产出库"
            },{
                "task_id": "124",
                "material_no": "a002",
                "pdm_no": null,  促进剂以外为空
                "batch_no": "1",
                "lot_no": "fffffff",
                "weight": 100.00,
                "unit": "kg",
                "product_time": "2020-10-28 14:39:17",
                "expire_time": "2021-10-28 14:39:17",
                "rfid": "20120741",
                "station": "出货口1",
                "out_user": "user1",
                "out_type": "生产出库"  
        }]
        }
        """
        pass


##############################################################