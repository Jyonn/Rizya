from SmartDjango import Packing, Analyse
from django.views import View

from Memory.models import Memory, Event, MemoryP
from Trigger.models import TriggerP


class BaseView(View):
    """ /api/memory """
    @staticmethod
    @Packing.http_pack
    def get(r):
        """获取纪念列表"""
        return Memory.objects.dict(Memory.d_list)

    @staticmethod
    @Packing.http_pack
    @Analyse.r(b=[MemoryP.TEXT, MemoryP.DATE, MemoryP.EVENT, TriggerP.TRIGGER_HUB])
    def post(r):
        """新增纪念日"""
        ret = Memory.create(**r.d.dict())
        if not ret.ok:
            return ret
        memory = ret.body  # type: Memory
        return memory.d()


class IdView(View):
    """ /api/memory/@:memory_id """
    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.MEMORY])
    def get(r, memory_id):
        """获取纪念日信息"""
        memory = r.d.memory  # type: Memory
        return memory.d()

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.MEMORY],
               b=[MemoryP.TEXT, MemoryP.DATE, MemoryP.EVENT, TriggerP.TRIGGER_HUB])
    def put(r, memory_id):
        """修改纪念日信息"""
        memory = r.d.memory  # type: Memory
        memory.update(**r.d.dict('text', 'date', 'event', 'trigger_hub'))

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.MEMORY])
    def delete(r, memory_id):
        """删除纪念日"""
        memory = r.d.memory  # type: Memory
        memory.remove()


class EventView(View):
    """ /api/memory/event """
    @staticmethod
    @Packing.http_pack
    def get(r):
        """获取事件列表"""
        return Event.objects.dict(Event.d)

    @staticmethod
    @Packing.http_pack
    @Analyse.r(b=[MemoryP.E_NAME])
    def post(r):
        """新增事件"""
        ret = Event.create(**r.d.dict())
        if not ret.ok:
            return ret
        event = ret.body  # type: Event
        return event.d()


class EventIdView(View):
    """ /api/memory/event/@:event_id """
    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.EVENT])
    def get(r, event_id):
        """查看事件信息"""
        event = r.d.event  # type: Event
        return event.d()

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.EVENT], b=[MemoryP.E_NAME])
    def put(r, evnet_id):
        """修改事件信息"""
        event = r.d.event  # type: Event
        event.update(**r.d.dict('name'))

    @staticmethod
    @Packing.http_pack
    @Analyse.r(a=[MemoryP.EVENT])
    def delete(r, event_id):
        """删除事件"""
        event = r.d.event  # type: Event
        event.remove()
