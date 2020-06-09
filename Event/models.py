import datetime

from SmartDjango import models, E
from django.utils.crypto import get_random_string
from lemoji import EMOJI_LIST


@E.register(id_processor=E.idp_cls_prefix())
class EventError:
    CREATE_TYPE = E("新建事件组失败")
    CREATE = E("添加事件失败")
    EMOJI = E("emoji表情错误")
    TYPE_NOT_FOUND = E("找不到事件组")
    TYPE_NOT_BELONG = E("事件组不属于此空间")
    NOT_FOUND = E("找不到此事件")
    BIND_ALBUM = E("已绑定相册")


class EventType(models.Model):
    """事件组"""
    etid = models.CharField(
        max_length=6,
        min_length=6,
        unique=True,
        verbose_name='事件组ID',
        default=None,
    )

    name = models.CharField(
        max_length=10,
        min_length=1,
        verbose_name='事件名称',
    )

    emoji = models.CharField(
        max_length=10,
        min_length=1,
        verbose_name='事件的emoji表示',
    )

    space = models.ForeignKey(
        'Space.Space',
        on_delete=models.CASCADE,
    )

    default_cover = models.ForeignKey(
        'Image.Image',
        on_delete=models.SET_NULL,
        null=True,
        related_name='default_cover'
    )

    current_cover = models.ForeignKey(
        'Image.Image',
        on_delete=models.SET_NULL,
        null=True,
        related_name='current_cover',
    )

    @classmethod
    def is_id_unique(cls, etid):
        try:
            cls.objects.get(etid=etid)
            return False
        except cls.DoesNotExist:
            return True

    @classmethod
    def generate_etid(cls):
        while True:
            etid = get_random_string(6)
            if cls.is_id_unique(etid):
                return etid

    @staticmethod
    def _valid_emoji(emoji):
        if emoji not in EMOJI_LIST:
            raise EventError.EMOJI

    @classmethod
    def get(cls, etid):
        try:
            return cls.objects.get(etid=etid)
        except Exception as err:
            raise EventError.TYPE_NOT_FOUND(debug_message=err)

    @classmethod
    def create(cls, **kwargs):
        try:
            return cls.objects.create(**kwargs, etid=cls.generate_etid())
        except Exception as err:
            raise EventError.CREATE_TYPE(debug_message=err)

    def belongs_to(self, space):
        if self.space != space:
            raise EventError.TYPE_NOT_BELONG

    def rename(self, name, emoji):
        self.name = name
        self.emoji = emoji
        self.save()

    def participate(self, **kwargs):
        try:
            return self.event_set.create(**kwargs, event_id=Event.generate_event_id())
        except Exception as err:
            raise EventError.CREATE(debug_message=err)

    def d(self):
        return self.dictify('name', 'emoji', 'etid')

    def delete(self, *args, **kwargs):
        if self.current_cover:
            self.current_cover.delete()
        if self.default_cover:
            self.default_cover.delete()
        super(EventType, self).delete(*args, **kwargs)


class EventTypeP:
    name, emoji, etid = EventType.get_params('name', 'emoji', 'etid')

    etid_getter = etid.clone().rename(
        'etid', yield_name='event_type', stay_origin=True).process(EventType.get)


class Event(models.Model):
    event_id = models.CharField(
        max_length=6,
        min_length=6,
        unique=True,
        default=None,
    )

    event_type = models.ForeignKey(
        EventType,
        on_delete=models.CASCADE,
    )

    start_date = models.DateField()

    duration = models.PositiveIntegerField(
        default=1
    )

    name = models.CharField(
        max_length=20,
    )

    album = models.ForeignKey(
        'Album.Album',
        on_delete=models.SET_NULL,
        null=True,
    )

    attends = models.ManyToManyField(
        'Space.SpaceMan',
    )

    @classmethod
    def get(cls, event_id):
        try:
            return cls.objects.get(event_id=event_id)
        except Exception:
            raise EventError.NOT_FOUND

    @classmethod
    def is_id_unique(cls, event_id):
        try:
            cls.objects.get(event_id=event_id)
            return False
        except cls.DoesNotExist:
            return True

    @classmethod
    def generate_event_id(cls):
        while True:
            event_id = get_random_string(6)
            if cls.is_id_unique(event_id):
                return event_id

    def update(self, name, duration, start_date):
        self.name = name
        self.duration = duration
        self.start_date = start_date
        self.save()

    def bind_album(self, album):
        if self.album:
            raise EventError.BIND_ALBUM
        self.album = album
        self.save()

    def _readable_album_id(self):
        if self.album:
            return self.album.res_id

    def _readable_start_date(self):
        return self.start_date.strftime('%Y-%m-%d')

    def d_et(self):
        return self.dictify('start_date', 'duration', 'name', 'album_id', 'event_id')


class EventP:
    event_id, start_date, duration, name = Event.get_params(
        'event_id', 'start_date', 'duration', 'name')
    id_getter = event_id.clone().rename(
        'event_id', yield_name='event', stay_origin=True).process(Event.get)
    start_date.process(lambda s: datetime.datetime.strptime(s, '%Y-%m-%d').date(), begin=True)
