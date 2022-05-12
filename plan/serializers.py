import datetime
import logging
from collections import OrderedDict

from django.db.transaction import atomic
from rest_framework import serializers

from basics.models import WorkSchedulePlan, Equip, GlobalCode, PlanSchedule
from mes.base_serializer import BaseModelSerializer
from mes.common_code import WebService
from mes.conf import COMMON_READ_ONLY_FIELDS, VERSION_EQUIP, hf_db
from plan.models import ProductDayPlan, ProductClassesPlan, MaterialDemanded, ProductBatchingClassesPlan
from plan.uuidfield import UUidTools
from production.models import TrainsFeedbacks, PlanStatus
from recipe.models import ProductBatching
from work_station.models import I_RECIPES_V, ProdOrdersImp, LogTable, I_RECIPE_COMPONENTS_V

logger = logging.getLogger('api_log')


class ProductClassesPlanManyCreateSerializer(BaseModelSerializer):
    """胶料日班次计划序列化"""

    classes_name = serializers.CharField(source='work_schedule_plan.classes.global_name', read_only=True)
    product_no = serializers.CharField(source='product_day_plan.product_batching.stage_product_batch_no',
                                       read_only=True)
    status = serializers.SerializerMethodField(read_only=True, help_text='计划状态')
    start_time = serializers.DateTimeField(source='work_schedule_plan.start_time', read_only=True)
    end_time = serializers.DateTimeField(source='work_schedule_plan.end_time', read_only=True)
    equip_no = serializers.CharField(source='product_day_plan.equip.equip_no', read_only=True)

    def get_status(self, obj):
        plan_status = PlanStatus.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('created_date').last()
        if plan_status:
            return plan_status.status
        else:
            return None

    class Meta:
        model = ProductClassesPlan
        exclude = ('product_day_plan',)
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def create(self, validated_data):
        instance = super().create(validated_data)
        # 创建计划状态
        PlanStatus.objects.create(plan_classes_uid=instance.plan_classes_uid, equip_no=instance.equip.equip_no,
                                  product_no=instance.product_batching.stage_product_batch_no,
                                  status='等待', operation_user=self.context['request'].user.username)
        # 创建原材料需求量
        for pbd_obj in instance.product_batching.batching_details.filter(delete_flag=False):
            MaterialDemanded.objects.create(product_classes_plan=instance,
                                            work_schedule_plan=instance.work_schedule_plan,
                                            material=pbd_obj.material,
                                            material_demanded=pbd_obj.actual_weight * instance.plan_trains,
                                            plan_classes_uid=instance.plan_classes_uid)

        return instance


class ProductClassesPlanCreateSerializer(BaseModelSerializer):
    classes_name = serializers.CharField(source='work_schedule_plan.classes.global_name', read_only=True)
    classes = serializers.PrimaryKeyRelatedField(queryset=GlobalCode.objects.all(),
                                                 help_text='班次id（公共代码）', write_only=True)

    class Meta:
        model = ProductClassesPlan
        exclude = ('product_day_plan', 'work_schedule_plan', 'plan_classes_uid', 'equip', 'product_batching', 'status')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class ProductDayPlanSerializer(BaseModelSerializer):
    """胶料日计划序列化"""
    pdp_product_classes_plan = ProductClassesPlanCreateSerializer(many=True,
                                                                  help_text="""
                                                                  {"sn":1,"plan_trains":1,"classes":班次id
                                                                  "time":"12.5","weight":1,"unit":1,"note":备注}
                                                                  """)
    equip_no = serializers.CharField(source='equip.equip_no', read_only=True, help_text='机台编号')
    category = serializers.CharField(source='equip.category', read_only=True, help_text='设备种类属性')
    product_no = serializers.CharField(source='product_batching.stage_product_batch_no', read_only=True,
                                       help_text='胶料编码')
    batching_weight = serializers.DecimalField(source='product_batching.batching_weight', decimal_places=2,
                                               max_digits=8,
                                               read_only=True, help_text='配料重量')
    production_time_interval = serializers.DecimalField(source='product_batching.production_time_interval',
                                                        read_only=True,
                                                        help_text='配料时间', decimal_places=2, max_digits=10)
    dev_type_name = serializers.CharField(source='product_batching.dev_type.global_name', read_only=True)
    product_batching = serializers.IntegerField(required=False)
    product_batch_no = serializers.CharField(required=False)
    product_version = serializers.IntegerField(required=False)

    class Meta:
        model = ProductDayPlan
        fields = ('id', 'equip', 'equip_no', 'category', 'plan_schedule',
                  'product_no', 'batching_weight', 'production_time_interval', 'product_batching',
                  'pdp_product_classes_plan', 'dev_type_name', 'product_batch_no', "product_version")
        read_only_fields = COMMON_READ_ONLY_FIELDS
        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=model.objects.filter(delete_flag=False),
        #         fields=('equip', 'product_batching', 'plan_schedule'),
        #         message="当天该机台已有相同的胶料计划数据，请修改后重试!"
        #     )
        # ]

    @atomic()
    def create(self, validated_data):
        equip = validated_data.get("equip")
        product_no = validated_data.pop("product_batch_no")
        product_info = product_no.split('-')
        try:
            stage = GlobalCode.objects.get(global_name=product_info[1], global_type__type_name='胶料段次')
        except:
            stage = None
        if VERSION_EQUIP[equip.equip_no] == "v3":
            precept = validated_data.pop("product_version")
            recipe_weight = I_RECIPE_COMPONENTS_V.objects.using("H-Z04").get(line_aggregate="Mixer2",
                                                                             recipe_number=product_no,
                                                                             recipe_version=precept).weight

            try:
                product_batching, _ = ProductBatching.objects.exclude(used_type=6).get_or_create(
                    defaults={"batching_weight": recipe_weight},
                    stage_product_batch_no=product_no,
                    used_type=4,
                    equip=equip,
                    stage=stage,
                )
            except Exception as e:
                raise serializers.ValidationError("无法根据Z04机台返回信息绑定配方")
        else:
            try:
                product_batching = ProductBatching.objects.exclude(used_type=6).get(
                    stage_product_batch_no=product_no,
                    equip=equip)
            except Exception as e:
                raise serializers.ValidationError("胶料信息异常,详情:{}".format(e))
        if product_batching.used_type != 4:
            raise serializers.ValidationError('该配方不是启用状态！')
        details = validated_data.pop('pdp_product_classes_plan', None)
        validated_data['created_user'] = self.context['request'].user
        # 创建胶料日计划
        validated_data["product_batching"] = product_batching
        instance = super().create(validated_data)
        # 创建胶料日班次班次计划和原材料需求量
        for detail in details:
            if not detail['plan_trains']:
                continue
            classes = detail.pop('classes')
            # 这里是只允许创建当前排班和下一个排班的计划
            # ps_obj = PlanSchedule.objects.filter(day_time=datetime.date.today(),
            #                                      work_schedule=instance.plan_schedule.work_schedule).first()
            # 这里是判断当前日期可能已经没有这个排班了
            # print(ps_obj)
            # if not ps_obj:
            #     raise serializers.ValidationError('当前时间已经没有此排班了')
            # wsp_obj = ps_obj.work_schedule_plan.all().filter(start_time__lte=datetime.datetime.now(),
            #                                                  end_time__gte=datetime.datetime.now()).first()
            # 判断当前是不是今天的工厂排班，不是的话取昨天的
            # if not wsp_obj:
            #     today = datetime.date.today()
            #     oneday = datetime.timedelta(days=1)
            #     yesterday = today - oneday
            #     ps_obj = PlanSchedule.objects.filter(day_time=yesterday,
            #                                          work_schedule=instance.plan_schedule.work_schedule).first()
            #     if not ps_obj:
            #         raise serializers.ValidationError('当前时间已经没有此排班了')
            #     wsp_obj = ps_obj.work_schedule_plan.all().filter(start_time__lte=datetime.datetime.now(),
            #                                                      end_time__gte=datetime.datetime.now()).first()

            # 再一次判断是怕排班有间隔
            # if not wsp_obj:
            #     raise serializers.ValidationError('当前时间不在排班时间内！！！')
            # # print(wsp_obj, wsp_obj.start_time, wsp_obj.end_time, wsp_obj.classes)
            # nest_wsp_obj = ps_obj.work_schedule_plan.all().filter(start_time__gte=wsp_obj.end_time).first()
            # # 这里就是判断当前的排班是不是最后一个班次 进而日期加1，来获取下一天的第一个班次
            # if not nest_wsp_obj:
            #     today = wsp_obj.plan_schedule.day_time
            #     # print(today)
            #     oneday = datetime.timedelta(days=1)
            #     tomorrow = today + oneday
            #     ps_obj = PlanSchedule.objects.filter(day_time=tomorrow,
            #                                          work_schedule=instance.plan_schedule.work_schedule).first()
            #     nest_wsp_obj = ps_obj.work_schedule_plan.all().filter(start_time__gte=wsp_obj.end_time).first()
            # print(nest_wsp_obj, nest_wsp_obj.start_time, nest_wsp_obj.end_time, nest_wsp_obj.classes)

            # work_schedule_plan = WorkSchedulePlan.objects.filter(classes=classes,
            #                                                      plan_schedule=instance.plan_schedule).first()
            # if work_schedule_plan not in [wsp_obj, nest_wsp_obj]:
            #     raise serializers.ValidationError(
            #         f'只允许创建当前班次和下一个班次的计划,当前班次为时间为{wsp_obj.start_time}至{wsp_obj.end_time}，是{wsp_obj.plan_schedule.day_time}的{wsp_obj.classes}')

            '''这里是之前做的 只允许创建当前的排班的计划
            ## 不允许创建上一个班次的计划，(ps:举例说明 比如现在是中班，那么今天的早班是创建不了的，今天之前的计划也是创建不了的)
            # 值允许创建当前班次的计划
            end_time = work_schedule_plan.end_time  # 取班次的结束时间
            start_time = work_schedule_plan.start_time
            now_time = datetime.datetime.now()
            if now_time > end_time:
                raise serializers.ValidationError(
                    f'{end_time.strftime("%Y-%m-%d")}的{work_schedule_plan.classes.global_name}的计划不允许现在创建，只允许创建当前班次的计划')
            if now_time > end_time or now_time < start_time:
                raise serializers.ValidationError(
                    f'{end_time.strftime("%Y-%m-%d")}的{work_schedule_plan.classes.global_name}的计划不允许现在创建，只允许创建当前班次的计划')
            '''
            # if not work_schedule_plan:
            #     raise serializers.ValidationError('暂无该班次排班数据')
            work_schedule_plan = validated_data['plan_schedule'].work_schedule_plan.filter(classes=classes).first()
            if not work_schedule_plan:
                raise serializers.ValidationError('暂无该班次排班数据')
            detail['plan_classes_uid'] = UUidTools.uuid1_hex(instance.equip.equip_no)
            detail['product_day_plan'] = instance
            detail['work_schedule_plan'] = work_schedule_plan
            detail['equip'] = instance.equip
            detail['product_batching'] = product_batching
            detail['status'] = '等待'
            # 不能依赖前端给你传的数据
            detail['weight'] = product_batching.batching_weight

            pcp_obj = ProductClassesPlan.objects.create(**detail, created_user=self.context['request'].user)
            # 创建计划状态
            PlanStatus.objects.create(plan_classes_uid=pcp_obj.plan_classes_uid, equip_no=instance.equip.equip_no,
                                      product_no=instance.product_batching.stage_product_batch_no,
                                      status='等待', operation_user=self.context['request'].user.username)
            for pbd_obj in instance.product_batching.batching_details.filter(delete_flag=False):
                MaterialDemanded.objects.create(product_classes_plan=pcp_obj,
                                                work_schedule_plan=pcp_obj.work_schedule_plan,
                                                material=pbd_obj.material,
                                                material_demanded=pbd_obj.actual_weight * pcp_obj.plan_trains,
                                                plan_classes_uid=pcp_obj.plan_classes_uid)
        return instance


class ProductBatchingClassesPlanSerializer(BaseModelSerializer):
    classes = serializers.CharField(source='classes_detail.classes.global_name', read_only=True)

    class Meta:
        model = ProductBatchingClassesPlan
        exclude = ('product_batching_day_plan', 'classes_detail')
        read_only_fields = COMMON_READ_ONLY_FIELDS


class PalletFeedbacksPlanSerializer(BaseModelSerializer):
    equip_name = serializers.CharField(source='equip.equip_no', read_only=True, help_text='机台名')
    stage_product_batch_no = serializers.CharField(source='product_batching.stage_product_batch_no',
                                                   read_only=True, help_text='胶料编码')
    classes = serializers.CharField(source='work_schedule_plan.classes.global_name', read_only=True, help_text='班次')
    actual_trains = serializers.SerializerMethodField(read_only=True, help_text='实际车次')
    operation_user = serializers.SerializerMethodField(read_only=True, help_text='操作员')
    status = serializers.SerializerMethodField(read_only=True, help_text='状态')
    day_time = serializers.DateField(source='work_schedule_plan.plan_schedule.day_time', read_only=True)
    group = serializers.CharField(source='work_schedule_plan.group.global_name', read_only=True, help_text='班组')
    # begin_time = serializers.DateTimeField(source='work_schedule_plan.start_time', read_only=True, help_text='开始时间')
    # end_time = serializers.DateTimeField(source='work_schedule_plan.end_time', read_only=True, help_text='结束时间')
    begin_time = serializers.SerializerMethodField(read_only=True, help_text='开始时间')
    end_time = serializers.SerializerMethodField(read_only=True, help_text='结束时间')
    classes_begin_time = serializers.DateTimeField(read_only=True, help_text='开始时间', source='work_schedule_plan.start_time')
    classes_end_time = serializers.DateTimeField(read_only=True, help_text='开始时间', source='work_schedule_plan.end_time')

    def get_begin_time(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('id').first()
        if tfb_obj:
            return tfb_obj.begin_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    def get_end_time(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('id').last()
        if tfb_obj:
            return tfb_obj.end_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None

    def get_actual_trains(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('created_date').last()
        if tfb_obj:
            return tfb_obj.actual_trains
        else:
            return None

    def get_operation_user(self, obj):
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('created_date').last()
        if tfb_obj:
            return tfb_obj.operation_user
        else:
            return None

    def get_status(self, obj):
        plan_status = PlanStatus.objects.filter(plan_classes_uid=obj.plan_classes_uid).order_by('created_date').last()
        if plan_status:
            return plan_status.status
        else:
            return None

    class Meta:
        model = ProductClassesPlan
        fields = '__all__'
        read_only_fields = COMMON_READ_ONLY_FIELDS


class UpRegulationSerializer(BaseModelSerializer):
    """上调"""
    equip_no = serializers.CharField(write_only=True, help_text='机台名', required=False)
    classes = serializers.CharField(write_only=True, help_text='班次', required=False)
    product_batching = serializers.CharField(write_only=True, help_text='配方', required=False)
    begin_times = serializers.DateTimeField(write_only=True, help_text='开始时间', required=False)
    end_times = serializers.DateTimeField(write_only=True, help_text='结束时间', required=False)

    class Meta:
        model = ProductClassesPlan
        fields = ('equip_no', 'classes', 'product_batching', 'begin_times', 'end_times')
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).order_by('created_date').last()
        # for p_obj in p_status:
        if p_status.status != '等待':
            raise serializers.ValidationError({'equip_no': '只有等待中的计划才能上调'})
        update_dict = {'delete_flag': False}
        equip_no = validated_data.get('equip_no', None)
        if equip_no:
            update_dict['product_day_plan__equip__equip_no'] = equip_no
        classes = validated_data.get('classes', None)
        if classes:
            update_dict['work_schedule_plan__classes__global_name'] = classes
        product_batching = validated_data.get('product_batching', None)
        if product_batching:
            update_dict['product_day_plan__product_batching__stage_product_batch_no'] = product_batching
        begin_times = validated_data.get('begin_times', None)
        end_times = validated_data.get('end_times', None)
        if begin_times and end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times,
                                                             end_time__lte=end_times)
        elif begin_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times)
        elif end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, end_time__lte=end_times)
        else:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict)
        last_obj = pcp_queryset.filter(sn__lt=instance.sn).order_by('sn').last()
        if last_obj:
            p_status = PlanStatus.objects.filter(plan_classes_uid=last_obj.plan_classes_uid).order_by(
                'created_date').last()
            if p_status.status != '等待':
                raise serializers.ValidationError({'equip_no': '被上调的计划只有等待中的才能上调'})
            snsn = last_obj.sn
            last_obj.sn = instance.sn
            last_obj.save()

            instance.sn = snsn
            instance.save()
            return instance
        raise serializers.ValidationError({'equip_name': '当前计划无法上调'})


class DownRegulationSerializer(BaseModelSerializer):
    """下调"""
    equip_no = serializers.CharField(write_only=True, help_text='机台名', required=False)
    classes = serializers.CharField(write_only=True, help_text='班次', required=False)
    product_batching = serializers.CharField(write_only=True, help_text='配方', required=False)
    begin_times = serializers.DateTimeField(write_only=True, help_text='开始时间', required=False)
    end_times = serializers.DateTimeField(write_only=True, help_text='结束时间', required=False)

    class Meta:
        model = ProductClassesPlan
        fields = ('equip_no', 'classes', 'product_batching', 'begin_times', 'end_times')
        read_only_fields = COMMON_READ_ONLY_FIELDS

    @atomic()
    def update(self, instance, validated_data):
        p_status = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).order_by('created_date').last()
        # for p_obj in p_status:
        if p_status.status != '等待':
            raise serializers.ValidationError({'equip_no': '只有等待中的计划才能下调'})
        update_dict = {'delete_flag': False}
        equip_no = validated_data.get('equip_no', None)
        if equip_no:
            update_dict['product_day_plan__equip__equip_no'] = equip_no
        classes = validated_data.get('classes', None)
        if classes:
            update_dict['work_schedule_plan__classes__global_name'] = classes
        product_batching = validated_data.get('product_batching', None)
        if product_batching:
            update_dict['product_day_plan__product_batching__stage_product_batch_no'] = product_batching
        begin_times = validated_data.get('begin_times', None)
        end_times = validated_data.get('end_times', None)
        if begin_times and end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times,
                                                             end_time__lte=end_times)
        elif begin_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, begin_time__gte=begin_times)
        elif end_times:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict, end_time__lte=end_times)
        else:
            pcp_queryset = ProductClassesPlan.objects.filter(**update_dict)
        last_obj = pcp_queryset.filter(sn__gt=instance.sn).order_by('sn').first()
        if last_obj:
            p_status = PlanStatus.objects.filter(plan_classes_uid=last_obj.plan_classes_uid).order_by(
                'created_date').last()
            if p_status.status != '等待':
                raise serializers.ValidationError({'equip_no': '被上调的计划只有等待中的才能下调'})
            snsn = last_obj.sn
            last_obj.sn = instance.sn
            last_obj.save()

            instance.sn = snsn
            instance.save()
            return instance
        raise serializers.ValidationError({'equip_name': '当前计划无法下调'})


class UpdateTrainsSerializer(BaseModelSerializer):
    '''修改车次和重传'''
    trains = serializers.IntegerField(write_only=True, help_text='修改车次')

    class Meta:
        model = ProductClassesPlan
        fields = ('trains',)
        read_only_fields = COMMON_READ_ONLY_FIELDS

    # @atomic()
    def update(self, instance, validated_data):
        if instance.product_day_plan.product_batching.used_type != 4:  # 4对应配方的启用状态
            raise serializers.ValidationError("该计划对应配方未启用,无法下达")
        # if validated_data.get('trains') - instance.plan_trains <= 2:
        #     raise serializers.ValidationError({'trains': "修改车次至少要比原车次大2次"})
        # 查询计划状态变更
        p_obj = PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).order_by('created_date').last()
        if not p_obj:
            raise serializers.ValidationError({'trains': "计划状态变更没有数据"})
        if p_obj.status != '运行中':
            raise serializers.ValidationError({'trains': '只有运行中的计划才可以修改车次'})
        # 查询车次产出反馈
        tfb_obj = TrainsFeedbacks.objects.filter(plan_classes_uid=instance.plan_classes_uid).order_by(
            'created_date').last()
        if not tfb_obj:
            pass
        else:
            if validated_data.get('trains') - tfb_obj.actual_trains < 2:
                raise serializers.ValidationError({'trains': "修改车次至少要比当前车次大于或等于2次"})
        trains = validated_data.get('trains')
        instance.plan_trains = trains
        instance.save()

        equip_no = instance.product_day_plan.equip.equip_no
        if "0" in equip_no and not equip_no.endswith('0'):
            ext_str = equip_no[-1]
        else:
            ext_str = equip_no[1:]
        version = VERSION_EQUIP[equip_no]
        if version == "v1":
            from work_station import models as md
            model_list = ['IfdownShengchanjihua', 'IfdownRecipeMix', 'IfdownPmtRecipe', "IfdownRecipeWeigh"]
            model_name = getattr(md, model_list[0] + ext_str)
            mid_plan_instance = model_name.objects.filter().first()
            if not mid_plan_instance:
                raise serializers.ValidationError({'trains': "异常接收状态,仅运行中状态允许修改车次"})
            if mid_plan_instance.recstatus == "车次需更新":
                recstatus = "车次需更新"
            elif mid_plan_instance.recstatus == "运行中":
                recstatus = "车次需更新"
            elif mid_plan_instance.recstatus == "配方车次需更新":
                recstatus = "配方车次需更新"
            elif mid_plan_instance.recstatus == '配方需重传':
                recstatus = "配方车次需更新"
            else:
                raise serializers.ValidationError({'trains': "等待状态中的计划，无法修改工作站车次"})
            mid_plan_instance.setno = trains
            mid_plan_instance.save()
            for model_str in model_list:
                model_name = getattr(md, model_str + ext_str)
                model_name.objects.all().update(recstatus=recstatus)
        elif version == "v2":
            data = OrderedDict()
            data['updatestate'] = instance.plan_trains
            data['planid'] = instance.plan_classes_uid
            data['no'] = ext_str
            try:
                WebService.issue(data, 'updatetrains', equip_no=ext_str, equip_name="上辅机")
            except Exception as e:
                raise serializers.ValidationError(f"上辅助连接超时|{e}")
        elif version == "v3":
            # 四号机只会有计划订单下达，所以单独写一块代码， 至于封装问题，等逻辑处理完再说
            recipe_name = instance.product_batching.stage_product_batch_no
            hf_recipe_version = instance.product_batching.precept
            if hf_recipe_version is None:
                hf_recipe_version = 1
            else:
                try:
                    hf_recipe_version = int(instance.product_batching.precept)
                except:
                    raise serializers.ValidationError("ZO4机台配方的版本/方案异常，请检查是否为标准数字")
            host_id = int(datetime.datetime.now().strftime('%Y%m%d%H%M%S')) // 111
            if ProdOrdersImp.objects.using(hf_db).filter(pori_line_name='Z04',
                                                         pori_order_number=instance.plan_classes_uid,
                                                         pori_recipe_code=recipe_name,
                                                         pori_recipe_version=hf_recipe_version,
                                                         pori_pror_status__in=[3]).exists():
                raise serializers.ValidationError("计划当前不可修改车次")
            try:
                I_RECIPES_V.objects.using("H-Z04").filter(recipe_blocked='no')

                ProdOrdersImp.objects.using(hf_db).filter(pori_line_name='Z04',
                                                          pori_order_number=instance.plan_classes_uid,
                                                          pori_recipe_code=recipe_name,
                                                          pori_recipe_version=hf_recipe_version).delete()
                ProdOrdersImp.objects.using(hf_db).create(
                    pori_line_name='Z04',
                    pori_order_number=instance.plan_classes_uid,
                    pori_recipe_code=recipe_name,
                    pori_recipe_version=hf_recipe_version,
                    pori_batch_quantity_set=instance.plan_trains,
                    pori_order_weight=instance.weight,
                    pori_pror_blocked=0,
                    pori_function=4,
                    pori_host_id=host_id
                )
            except Exception as e:
                lt = LogTable.objects.using(hf_db).filter(lgtb_host_id=host_id).order_by("lgtb_id").last()
                raise serializers.ValidationError(f"{lt.lgtb_sql_errormessage}||{lt.lgtb_pks_errormessage}")
            else:
                plan_status = ProdOrdersImp.objects.using(hf_db).filter(pori_line_name='Z04',
                                                                        pori_order_number=instance.plan_classes_uid,
                                                                        pori_recipe_code=recipe_name,
                                                                        pori_recipe_version=hf_recipe_version).order_by(
                    "pori_id").last().pori_status
                if plan_status < 0:
                    lt = LogTable.objects.using(hf_db).filter(lgtb_host_id=host_id).order_by("lgtb_id").last()
                    raise serializers.ValidationError(f"{lt.lgtb_sql_errormessage}||{lt.lgtb_pks_errormessage}")
        else:
            data = OrderedDict()
            data['updatestate'] = instance.plan_trains
            data['planid'] = instance.plan_classes_uid
            data['no'] = ext_str
            try:
                WebService.issue(data, 'updatetrains', equip_no=ext_str, equip_name="上辅机")
            except Exception as e:
                raise serializers.ValidationError(f"上辅助连接超时|{e}")
        return instance


class ProductDayPlanSyncInterface(serializers.ModelSerializer):
    product_batching = serializers.CharField(source='product_batching.stage_product_batch_no')
    plan_schedule = serializers.CharField(source='plan_schedule.plan_schedule_no')
    equip = serializers.CharField(source='equip.equip_no')

    class Meta:
        model = ProductDayPlan
        fields = ('equip', 'product_batching', 'plan_schedule')


class PlanReceiveSerializer(serializers.ModelSerializer):
    equip = serializers.CharField()
    work_schedule_plan = serializers.CharField()
    product_batching = serializers.CharField()
    # product_day_plan = ProductDayPlanSyncInterface()

    @atomic()
    def validate(self, attrs):
        work_schedule_plan = attrs.get('work_schedule_plan')
        product_batching = attrs.get('product_batching')
        equip = attrs.get('equip')
        # plan_schedule = attrs.get('product_day_plan')['plan_schedule']['plan_schedule_no']
        try:
            equip = Equip.objects.get(equip_no=equip, delete_flag=False)
            work_schedule_plan = WorkSchedulePlan.objects.get(work_schedule_plan_no=work_schedule_plan,
                                                              delete_flag=False)
            # plan_schedule = PlanSchedule.objects.get(plan_schedule_no=plan_schedule, delete_flag=False)
        except Equip.DoesNotExist:
            raise serializers.ValidationError('上辅机机台{}不存在，请MES下发该数据'.format(attrs.get('equip')))
        except WorkSchedulePlan.DoesNotExist:
            raise serializers.ValidationError('上辅机排班详情{}不存在，请MES下发该数据'.format(attrs.get('work_schedule_plan')))
        # except ProductBatching.DoesNotExist:
        #     raise serializers.ValidationError('上辅机胶料配料标准{}不存在，请MES下发该数据'.format(attrs.get('product_batching')))
        # except PlanSchedule.DoesNotExist:
        #     raise serializers.ValidationError(
        #         '上辅机排班管理{}不存在，请MES下发该数据'.format(attrs.get('product_day_plan')['plan_schedule']['plan_schedule_no']))
        except Exception as e:
            logger.error(e)
            raise serializers.ValidationError("相关表数据错误")

        product_batching = ProductBatching.objects.exclude(used_type=6).filter(
            stage_product_batch_no=product_batching, delete_flag=False, batching_type=1, equip=equip).last()
        # 下面的三个注释就不要看了  群控这边直接计划关联机台配方 没有机台配方就报错
        # 暂时将batching_type=2去掉 把first改为last
        # 原因：mes配方下达batching_type=2 计划是和这个关联
        # 但是如果在下发计划之前复制了配方batching_type是1，这个时候下发计划应该是和复制之后的配方关联 下面也是
        if not product_batching:
            raise serializers.ValidationError('上辅机群控系统暂无{}机台配方：{}，请新建后重试！'.format(equip.equip_no,
                                                                                  attrs.get('product_batching')))
        if product_batching.used_type != 4:
            raise serializers.ValidationError('上辅机群控系统{}机台配方{}尚未启用，请修改后重试！'.format(equip.equip_no,
                                                                                    attrs.get('product_batching')))
        attrs['product_batching'] = product_batching
        # 判断胶料日计划是否存在 不存在则创建
        # pdp_dict = attrs.get('product_day_plan')
        pb_obj = ProductBatching.objects.exclude(used_type=6).filter(
            stage_product_batch_no=product_batching.stage_product_batch_no,
            delete_flag=False, batching_type=1, equip=equip).last()
        if not pb_obj:
            raise serializers.ValidationError(
                '{}在群控上没有同名的机台配方'.format(product_batching.stage_product_batch_no))
        # 校验胶料日计划设备
        # pdp_obj = ProductDayPlan.objects.filter(equip=equip, product_batching=pb_obj,
        #                                         plan_schedule=plan_schedule).first()
        # if pdp_obj:
        #     attrs['product_day_plan'] = pdp_obj
        # else:
        #     attrs['product_day_plan'] = ProductDayPlan.objects.create(equip=equip, product_batching=pb_obj,
        #                                                               plan_schedule=plan_schedule)
        attrs['work_schedule_plan'] = work_schedule_plan
        attrs['equip'] = equip
        attrs['status'] = '等待'
        # 因为计划里的时间重量都是通过配方a算出来的  下发给上辅机 上辅机复制配方a为配方b 这个时候计划是需要跟配方b关联的 计划的时间重量就要重新计算
        if product_batching.production_time_interval:
            attrs['time'] = attrs['plan_trains'] * product_batching.production_time_interval
        else:
            attrs['time'] = None
        attrs['weight'] = attrs['plan_trains'] * product_batching.batching_weight
        return attrs

    @atomic()
    def create(self, validated_data):
        pcp_obj = ProductClassesPlan.objects.filter(plan_classes_uid=validated_data['plan_classes_uid'],
                                                    delete_flag=False).first()
        if pcp_obj:
            plan_status = PlanStatus.objects.filter(plan_classes_uid=pcp_obj.plan_classes_uid).order_by(
                'created_date').last()
            if plan_status.status not in ["完成", "等待"]:
                raise serializers.ValidationError('该计划{}在上辅机处于非等待或完成状态，不可再下达'.format(pcp_obj.plan_classes_uid))
            instance = super().update(pcp_obj, validated_data)
            PlanStatus.objects.filter(plan_classes_uid=instance.plan_classes_uid).update(
                equip_no=instance.equip.equip_no,
                product_no=instance.product_batching.stage_product_batch_no)
            # MaterialDemanded.objects.filter(product_classes_plan=instance).update(delete_flag=True)
            # for pbd_obj in instance.product_batching.batching_details.filter(delete_flag=False):
            #     MaterialDemanded.objects.create(product_classes_plan=instance,
            #                                     work_schedule_plan=instance.work_schedule_plan,
            #                                     material=pbd_obj.material,
            #                                     material_demanded=pbd_obj.actual_weight * instance.plan_trains,
            #                                     plan_classes_uid=instance.plan_classes_uid)
        else:
            instance = super().create(validated_data)
            # 创建计划状态
            PlanStatus.objects.create(plan_classes_uid=instance.plan_classes_uid, equip_no=instance.equip.equip_no,
                                      product_no=instance.product_batching.stage_product_batch_no,
                                      status='等待', operation_user=self.context['request'].user.username)
            # 创建原材料需求量
            # for pbd_obj in instance.product_batching.batching_details.filter(delete_flag=False):
            #     MaterialDemanded.objects.create(product_classes_plan=instance,
            #                                     work_schedule_plan=instance.work_schedule_plan,
            #                                     material=pbd_obj.material,
            #                                     material_demanded=pbd_obj.actual_weight * instance.plan_trains,
            #                                     plan_classes_uid=instance.plan_classes_uid)
        return instance

    class Meta:
        model = ProductClassesPlan
        fields = ('sn', 'plan_trains', 'time', 'weight', 'unit', 'work_schedule_plan',
                  'plan_classes_uid', 'note', 'equip',
                  'product_batching',)
        read_only_fields = COMMON_READ_ONLY_FIELDS
