import datetime

from SmartDjango import SmartModel, Packing, ErrorCenter, E, Param
from django.db import models


class TriggerE(ErrorCenter):
    TRIGGER_HUB_NOT_FOUND = E("找不到触发库", hc=404)
    TRIGGER_NOT_FOUND = E("找不到触发器", hc=404)
    UNFIT = E("没有触发", hc=200)
    INVALID_DAYS = E("天数至少为1天", hc=403)
    CREATE_TRIGGER = E("新建触发器失败", hc=500)
    CREATE_TRIGGER_HUB = E("新建触发库失败", hc=500)


TriggerE.register()


class Trigger(SmartModel):
    """
    触发器类，用于判别距离日期的特殊意义
    """
    MAX_L = {
        'name': 20,
    }

    TTYPE_SOLID = 0
    TTYPE_TIMES = 1
    TTYPE_YEARS = 2
    TTYPE_CHOICES = (
        (TTYPE_SOLID, '固定天数'),
        (TTYPE_TIMES, '天数的倍数'),
        (TTYPE_YEARS, '周年'),
    )

    name = models.CharField(
        verbose_name='触发名称',
        max_length=MAX_L['name'],
    )

    ttype = models.PositiveSmallIntegerField(
        verbose_name='触发类型',
        choices=TTYPE_CHOICES,
    )

    days = models.PositiveIntegerField(
        verbose_name='天数',
    )

    """
    字段校验方法
    """
    @staticmethod
    @Packing.pack
    def _valid_days(days):
        if days <= 0:
            return TriggerE.INVALID_DAYS

    """
    增删方法
    """
    @classmethod
    @Packing.pack
    def create(cls, name, ttype, days):
        try:
            trigger = cls(
                name=name,
                ttype=ttype,
                days=days,
            )
        except Exception as err:
            return TriggerE.CREATE_TRIGGER
        return trigger

    def update(self, name, ttype, days):
        self.name = name
        self.ttype = ttype
        self.days = days
        self.save()

    def remove(self):
        self.delete()

    """
    字典方法
    """

    def _readable_id(self):
        return self.pk

    def d(self):
        return self.dictor(['name', 'ttype', 'days', 'id'])

    """
    查询方法
    """
    @Packing.pack
    def fit(self, crt_date: datetime.date, m_date: datetime.date):
        days = (crt_date - m_date).days + 1

        if self.ttype == self.TTYPE_SOLID:
            if self.days == days:
                return dict(ttype=self.ttype, days=days)
        elif self.ttype == self.TTYPE_TIMES:
            if days % self.days == 0:
                return dict(ttype=self.ttype, days=days, times=days / self.days)
        elif self.ttype == self.TTYPE_YEARS:
            if crt_date.month == m_date.month and crt_date.day == m_date.day and crt_date.year != m_date.year:
                return dict(ttype=self.ttype, years=crt_date.year - m_date.year)
        return TriggerE.UNFIT

    @classmethod
    @Packing.pack
    def get_by_pk(cls, pk):
        try:
            trigger = cls.objects.get(pk=pk)
        except cls.DoesNotExist as err:
            return TriggerE.TRIGGER_NOT_FOUND
        return trigger


class TriggerHub(SmartModel):
    MAX_L = {
        'name': 20,
    }

    name = models.CharField(
        verbose_name='触发库名称',
        max_length=MAX_L['name'],
    )

    triggers = models.ManyToManyField(
        'Trigger.Trigger',
        verbose_name='所属触发器',
    )

    """
    修改方法
    """

    def clear_triggers(self):
        self.triggers.clear()

    def update_triggers(self, triggers):
        self.clear_triggers()
        self.triggers.add(*triggers)

    """
    增删方法
    """

    @classmethod
    @Packing.pack
    def create(cls, name, triggers):
        try:
            hub = cls(
                name=name,
            )
            hub.save()
            hub.update_triggers(triggers)
        except Exception as err:
            return TriggerE.CREATE_TRIGGER_HUB
        return hub

    def update(self, name, triggers):
        self.name = name
        self.update_triggers(triggers)
        self.save()

    def remove(self):
        self.delete()

    """
    字典方法
    """

    def _readable_triggers(self):
        return list(map(Trigger.d, self.triggers.all()))

    def _readable_id(self):
        return self.pk

    def d(self):
        return self.dictor(['name', 'triggers', 'id'])

    """
    查询方法
    """
    @classmethod
    @Packing.pack
    def get_by_pk(cls, pk):
        try:
            trigger_hub = cls.objects.get(pk=pk)
        except cls.DoesNotExist as err:
            return TriggerE.TRIGGER_HUB_NOT_FOUND
        return trigger_hub


class TriggerP:
    T_NAME, TTYPE, DAYS = Trigger.P(['name', 'ttype', 'days'])
    TH_NAME, TRIGGERS = TriggerHub.P(['name', 'triggers'])
    TRIGGERS.process(lambda pks: Trigger.objects.filter(pk__in=pks))

    TRIGGER = Param('trigger_id', '触发器ID', 'trigger').process(Trigger.get_by_pk)
    TRIGGER_HUB = Param('trigger_hub_id', '触发库ID', 'trigger_hub').process(TriggerHub.get_by_pk)
