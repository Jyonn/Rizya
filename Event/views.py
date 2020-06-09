from SmartDjango import Analyse
from django.views import View

from Album.models import AlbumP
from Event.models import EventType, EventTypeP, Event, EventP
from Space.models import SpaceP


space_getter = SpaceP.space_getter.clone().rename('space', stay_origin=True)


class EventTypeView(View):
    """/event/types"""

    @staticmethod
    @Analyse.r(q=[space_getter])
    def get(r):
        """获取事件组"""
        return r.d.space.eventtype_set.dict(EventType.d)

    @staticmethod
    @Analyse.r(q=[space_getter], b=[EventTypeP.name, EventTypeP.emoji])
    def post(r):
        """新增事件组"""
        return EventType.create(**r.d.dict()).d()


class EventTypeIDView(View):
    """/event/types/:etid"""
    @staticmethod
    @Analyse.r(
        a=[EventTypeP.etid_getter],
        b=[EventTypeP.name, EventTypeP.emoji]
    )
    def put(r):
        """修改事件组"""
        r.d.event_type.rename(**r.d.dict('emoji', 'name'))

    @staticmethod
    @Analyse.r(a=[EventTypeP.etid_getter])
    def delete(r):
        """删除事件组"""
        r.d.event_type.delete()


class EventView(View):
    """/event/"""
    @staticmethod
    @Analyse.r(q=[EventTypeP.etid_getter])
    def get(r):
        """获取事件组的事件"""
        return r.d.event_type.event_set.dict(Event.d_et)

    @staticmethod
    @Analyse.r(q=[EventTypeP.etid_getter], b=[EventP.name, EventP.start_date, EventP.duration])
    def post(r):
        """新增事件"""
        event_type = r.d.event_type  # type: EventType
        event = event_type.participate(**r.d.dict('name', 'start_date', 'duration'))
        return event.d_et()


class EventIDView(View):
    """/event/:event_id"""
    @staticmethod
    @Analyse.r(
        a=[EventP.id_getter],
        b=[EventP.name, EventP.duration, EventP.start_date]
    )
    def put(r):
        """修改事件"""
        r.d.event.update(**r.d.dict('name', 'duration', 'start_date'))

    @staticmethod
    @Analyse.r(a=[EventP.id_getter])
    def delete(r):
        """删除事件"""
        r.d.event.delete()


class EventAlbumView(View):
    """/event/:event_id/album"""
    @staticmethod
    @Analyse.r(a=[EventP.id_getter], b=[AlbumP.id_getter])
    def put(r):
        """绑定相册"""
        r.d.event.bind_album(r.d.album)
