from SmartDjango import Analyse
from django.views import View

from Memory.models import Memory, Event, MemoryP
from Trigger.models import TriggerP


class BaseView(View):
    """ /api/memory """
    @staticmethod
    def get(_):
        """获取纪念列表"""
        return Memory.objects.dict(Memory.d_list)

    @staticmethod
    @Analyse.r(b=[MemoryP.text, MemoryP.date, MemoryP.event, TriggerP.trigger_hub])
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
    @Analyse.r(a=[MemoryP.memory])
    def get(r):
        """获取纪念日信息"""
        memory = r.d.memory  # type: Memory
        return memory.d()

    @staticmethod
    @Analyse.r(a=[MemoryP.memory],
               b=[MemoryP.text, MemoryP.date, MemoryP.event, TriggerP.trigger_hub])
    def put(r):
        """修改纪念日信息"""
        memory = r.d.memory  # type: Memory
        memory.update(**r.d.dict('text', 'date', 'event', 'trigger_hub'))

    @staticmethod
    @Analyse.r(a=[MemoryP.memory])
    def delete(r):
        """删除纪念日"""
        memory = r.d.memory  # type: Memory
        memory.remove()


class EventView(View):
    """ /api/memory/event """
    @staticmethod
    def get(_):
        """获取事件列表"""
        return Event.objects.dict(Event.d)

    @staticmethod
    @Analyse.r(b=[MemoryP.e_name])
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
    @Analyse.r(a=[MemoryP.event])
    def get(r):
        """查看事件信息"""
        event = r.d.event  # type: Event
        return event.d()

    @staticmethod
    @Analyse.r(a=[MemoryP.event], b=[MemoryP.e_name])
    def put(r):
        """修改事件信息"""
        event = r.d.event  # type: Event
        event.update(**r.d.dict('name'))

    @staticmethod
    @Analyse.r(a=[MemoryP.event])
    def delete(r):
        """删除事件"""
        event = r.d.event  # type: Event
        event.remove()
