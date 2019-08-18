from django.urls import path

from Memory.views import BaseView, IdView, EventView, EventIdView

urlpatterns = [
    path('', BaseView.as_view()),
    path('@<memory_id: int>', IdView.as_view()),
    path('event', EventView.as_view()),
    path('event/@<event_id: int>', EventIdView.as_view()),
]
