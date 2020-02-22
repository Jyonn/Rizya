from SmartDjango import Analyse
from django.views import View

from Event.models import EventType, EventTypeP, Event, EventP
from Space.models import SpaceP


space_getter = SpaceP.name_getter.clone().rename('space', stay_origin=True)


class EventTypeView(View):
    """/event/types"""

    @staticmethod
    @Analyse.r(q=[space_getter])
    def get(r):
        return r.d.space.eventtype_set.dict(EventType.d)

    @staticmethod
    @Analyse.r(q=[space_getter], b=[EventTypeP.name, EventTypeP.emoji])
    def post(r):
        return EventType.create(**r.d.dict()).d()


class EventTypeIDView(View):
    @staticmethod
    @Analyse.r(
        a=[EventTypeP.etid_getter],
        b=[EventTypeP.name, EventTypeP.emoji]
    )
    def put(r):
        r.d.event_type.rename(**r.d.dict('emoji', 'name'))

    @staticmethod
    @Analyse.r(a=[EventTypeP.etid_getter])
    def delete(r):
        r.d.event_type.remove()


class EventView(View):
    @staticmethod
    @Analyse.r(q=[EventTypeP.etid_getter])
    def get(r):
        return r.d.event_type.event_set.dict(Event.d_et)

    @staticmethod
    @Analyse.r(q=[EventTypeP.etid_getter], b=[EventP.name, EventP.start_date, EventP.duration])
    def post(r):
        event_type = r.d.event_type  # type: EventType
        event = event_type.participate(**r.d.dict('name', 'start_date', 'duration'))
        return event.d_et()


class EventIDView(View):
    @staticmethod
    @Analyse.r(a=[EventP.id_getter], b=[EventP.name, EventP.duration, EventP.start_date])
    def put(r):
        r.d.event.update(**r.d.dict('name', 'duration', 'start_date'))

    @staticmethod
    @Analyse.r(a=[EventP.id_getter])
    def delete(r):
        r.d.event.remove()
