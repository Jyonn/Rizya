from SmartDjango import Analyse
from django.views import View

from Trigger.models import Trigger, TriggerP, TriggerHub


class BaseView(View):
    """ /api/trigger """
    @staticmethod
    def get(_):
        """获取触发器列表"""
        return Trigger.objects.dict(Trigger.d)

    @staticmethod
    @Analyse.r(b=[TriggerP.t_name, TriggerP.ttype, TriggerP.days])
    def post(r):
        """新增触发器"""
        trigger = Trigger.create(**r.d.dict())
        return trigger.d()


class IdView(View):
    """ /api/trigger/@:trigger_id """
    @staticmethod
    @Analyse.r(a=[TriggerP.trigger])
    def get(r):
        """获取触发器信息"""
        trigger = r.d.trigger  # type: Trigger
        return trigger.d()

    @staticmethod
    @Analyse.r(a=[TriggerP.trigger], b=[TriggerP.th_name, TriggerP.ttype, TriggerP.days])
    def put(r):
        """修改触发器信息"""
        trigger = r.d.trigger  # type: Trigger
        trigger.update(**r.d.dict('name', 'ttype', 'days'))

    @staticmethod
    @Analyse.r(a=[TriggerP.trigger])
    def delete(r):
        """删除触发器"""
        trigger = r.d.trigger  # type: Trigger
        trigger.remove()


class HubView(View):
    """ /api/trigger/hub """
    @staticmethod
    def get(_):
        """获取触发库列表"""
        return TriggerHub.objects.dict(TriggerHub.d)

    @staticmethod
    @Analyse.r(b=[TriggerP.th_name, TriggerP.triggers])
    def post(r):
        """新建触发库"""
        trigger_hub = TriggerHub.create(**r.d.dict())
        return trigger_hub.d()


class HubIdView(View):
    """ /api/trigger/hub/@<trigger_hub_id: int> """
    @staticmethod
    @Analyse.r(a=[TriggerP.trigger_hub])
    def get(r):
        """获取触发库信息"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        return trigger_hub.d()

    @staticmethod
    @Analyse.r(a=[TriggerP.trigger_hub], b=[TriggerP.th_name, TriggerP.triggers])
    def put(r):
        """添加触发库"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        trigger_hub.update(**r.d.dict('name', 'triggers'))

    @staticmethod
    @Analyse.r(a=[TriggerP.trigger_hub])
    def delete(r):
        """删除触发库"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        trigger_hub.remove()
