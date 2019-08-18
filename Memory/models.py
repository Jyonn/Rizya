import datetime

from SmartDjango import SmartModel, Packing, ErrorCenter, E, Param
from django.db import models

from Trigger.models import TriggerHub, Trigger


class MemoryE(ErrorCenter):
    INVALID_DATE = E("不能是未来的日期", hc=403)
    EVENT_NOT_FOUND = E("找不到事件", hc=404)
    CREATE_EVENT = E("添加事件失败", hc=500)
    MEMORY_NOT_FOUND = E("找不到纪念日", hc=404)
    CREATE_MEMORY = E("添加纪念日失败", hc=500)


MemoryE.register()


class Event(SmartModel):
    MAX_L = {
        'name': 20,
    }

    name = models.CharField(
        verbose_name='事件名称',
        max_length=MAX_L['name'],
    )

    """
    增删方法
    """
    @classmethod
    @Packing.pack
    def create(cls, name):
        try:
            event = cls(
                name=name,
            )
            event.save()
        except Exception as err:
            return MemoryE.CREATE_EVENT
        return event

    def update(self, name):
        self.name = name
        self.save()

    def remove(self):
        self.delete()

    """
    字典方法
    """
    def _readable_id(self):
        return self.pk

    def d(self):
        return self.dictor(['name', 'id'])

    """
    查询方法
    """
    @classmethod
    @Packing.pack
    def get_by_pk(cls, pk):
        try:
            event = cls.objects.get(pk=pk)
        except cls.DoesNotExist as err:
            return MemoryE.EVENT_NOT_FOUND
        return event


class Memory(SmartModel):
    event = models.ForeignKey(
        'Memory.Event',
        verbose_name='纪念事件',
        on_delete=models.SET_NULL,
        null=True,
    )

    date = models.DateField(
        verbose_name='纪念日',
    )

    text = models.TextField(
        verbose_name='事件记录',
    )

    trigger_hub = models.ForeignKey(
        'Trigger.TriggerHub',
        on_delete=models.SET_NULL,
        null=True,
    )

    """
    校验方法
    """
    @staticmethod
    @Packing.pack
    def _valid_date(date: datetime.date):
        crt_date = datetime.date.today()
        if date > crt_date:
            return MemoryE.INVALID_DATE

    """
    增删方法
    """

    @classmethod
    @Packing.pack
    def create(cls, event: Event, date: datetime.date, text: str, trigger_hub: TriggerHub):
        try:
            memory = cls(
                event=event,
                date=date,
                text=text,
                trigger_hub=trigger_hub,
            )
            memory.save()
        except Exception as err:
            return MemoryE.CREATE_MEMORY
        return memory

    def update(self, event, date, text, trigger_hub):
        self.event = event
        self.date = date
        self.text = text
        self.trigger_hub = trigger_hub
        self.save()

    def remove(self):
        self.delete()

    """
    查询方法
    """

    @classmethod
    @Packing.pack
    def get_by_pk(cls, pk):
        try:
            memory = cls.objects.get(pk=pk)
        except cls.DoesNotExist as err:
            return MemoryE.MEMORY_NOT_FOUND
        return memory

    def fitting(self):
        crt_date = datetime.date.today()

        for trigger in self.trigger_hub.triggers.all():
            ret = trigger.fit(crt_date, self.date)
            if ret.ok:
                from Message.models import Message
                Message.create(self, Param.Classify(ret.body))
                break

    """
    字典方法
    """

    def _readable_id(self):
        return self.pk

    def _readable_days(self):
        crt_date = datetime.date.today()
        return (crt_date - self.date).days + 1

    def d(self):
        return self.dictor(['id', 'date', 'text', 'trigger_hub'])

    def d_msg(self):
        return self.dictor(['date', 'text'])

    def d_list(self):
        return self.dictor(['id', 'date', 'text'])


class MemoryP:
    E_NAME, = Event.P(['name'])
    EVENT = Param('event_id', '事件ID', 'event').process(Event.get_by_pk)

    TEXT, DATE = Memory.P(['text', 'date'])
    DATE.process(lambda d: datetime.datetime.strptime(d, '%Y-%m-%d').date(), begin=True)

    MEMORY = Param('memory_id', '纪念ID', 'memory').process(Memory.get_by_pk)
