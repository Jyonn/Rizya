import datetime

from SmartDjango import models, Excp, E, Param

from Memory.models import Memory
from Trigger.models import Trigger


@E.register
class MessageE:
    CREATE_MESSAGE = E("新建消息失败", hc=500)


class Message(models.Model):
    memory = models.ForeignKey(
        'Memory.Memory',
        on_delete=models.CASCADE,
        verbose_name='提醒的纪念',
    )

    ttype = models.PositiveSmallIntegerField(
        verbose_name='触发类型',
        choices=Trigger.TTYPE_CHOICES,
    )

    days = models.PositiveIntegerField(
        verbose_name='天数',
        null=True,
        default=None,
    )

    times = models.PositiveIntegerField(
        verbose_name='倍数',
        null=True,
        default=True,
    )

    years = models.PositiveIntegerField(
        verbose_name='周年',
        null=True,
        default=True,
    )

    create_date = models.DateField(
        verbose_name='创建时间',
    )

    read = models.BooleanField(
        verbose_name='是否已读',
        default=False,
    )

    """
    增删方法
    """

    @classmethod
    @Excp.pack
    def create(cls, memory: Memory, data: Param.Classify):
        crt_date = datetime.date.today()

        try:
            message = cls(
                memory=memory,
                create_date=crt_date,
                read=False,
                **data.dict(),
            )
            message.save()
        except Exception:
            return MessageE.CREATE_MESSAGE
        return message

    """
    字典方法
    """
    def _readable_memory(self):
        return self.memory.d_msg()

    def _readable_create_date(self):
        return self.create_date.strftime('%Y-%m-%d')

    def d(self):
        return self.dictor('memory', 'ttype', 'days', 'times', 'years', 'create_date', 'read')

    """
    修改方法
    """
    def reading(self):
        self.read = True
        self.save()
