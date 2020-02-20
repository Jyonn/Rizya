from SmartDjango import models


class EventType(models.Model):
    name = models.CharField(
        max_length=10,
        min_length=1,
        verbose_name='事件名称',
    )

    emoji = models.CharField(
        max_length=1,
        min_length=1,
        verbose_name='事件的emoji表示',
    )

    space = models.ForeignKey(
        'Space.Space',
        on_delete=models.CASCADE,
    )

    cover = models.CharField(
        max_length=512,
    )


class Event(models.Model):
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
    )

    start_date = models.DateField()

    duration = models.PositiveIntegerField(default=1)

    name = models.CharField(
        max_length=10,
    )
