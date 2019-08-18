from SmartDjango import Packing, Analyse
from django.views import View

from Trigger.models import Trigger, TriggerP, TriggerHub


class BaseView(View):
    """ /api/trigger """
    @staticmethod
    @Packing.http_pack
    def get(r):
        """获取触发器列表"""
        return Trigger.objects.dict(Trigger.d)

    @staticmethod
    @Packing.http_pack
    @Analyse.r(b=[TriggerP.T_NAME, TriggerP.TTYPE, TriggerP.DAYS])
    def post(r):
        """新增触发器"""
        ret = Trigger.create(**r.d.dict())
        if not ret.ok:
            return ret
        trigger = ret.body  # type: Trigger
        return trigger.d()


class IdView(View):
    """ /api/trigger/@:trigger_id """
    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER])
    def get(r, trigger_id):
        """获取触发器信息"""
        trigger = r.d.trigger  # type: Trigger
        return trigger.d()

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER], b=[TriggerP.TH_NAME, TriggerP.TTYPE, TriggerP.DAYS])
    def put(r, trigger_id):
        """修改触发器信息"""
        trigger = r.d.trigger  # type: Trigger
        trigger.update(**r.d.dict('name', 'ttype', 'days'))

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER])
    def delete(r, trigger_id):
        """删除触发器"""
        trigger = r.d.trigger  # type: Trigger
        trigger.remove()


class HubView(View):
    """ /api/trigger/hub """
    @staticmethod
    @Packing.http_pack
    def get(r):
        """获取触发库列表"""
        return TriggerHub.objects.dict(TriggerHub.d)

    @staticmethod
    @Packing.http_pack
    @Analyse.r(b=[TriggerP.TH_NAME, TriggerP.TRIGGERS])
    def post(r):
        """新建触发库"""
        ret = TriggerHub.create(**r.d.dict())
        if not ret.ok:
            return ret
        trigger_hub = ret.body  # type: TriggerHub
        return trigger_hub.d()


class HubIdView(View):
    """ /api/trigger/hub/@<trigger_hub_id: int> """
    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER_HUB])
    def get(r, trigger_hub_id):
        """获取触发库信息"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        return trigger_hub.d()

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER_HUB], b=[TriggerP.TH_NAME, TriggerP.TRIGGERS])
    def put(r, trigger_hub_id):
        """添加触发库"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        trigger_hub.update(**r.d.dict('name', 'triggers'))

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[TriggerP.TRIGGER_HUB])
    def delete(r, trigger_hub_id):
        """删除触发库"""
        trigger_hub = r.d.trigger_hub  # type: TriggerHub
        trigger_hub.remove()
