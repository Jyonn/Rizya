from django.urls import path

from Event.views import EventView, EventTypeView, EventTypeIDView, EventIDView, EventAlbumView

urlpatterns = [
    path('types', EventTypeView.as_view()),
    path('type/@<str:etid>', EventTypeIDView.as_view()),
    path('', EventView.as_view()),
    path('@<str:event_id>', EventIDView.as_view()),
    path('@<str:event_id>/album', EventAlbumView.as_view()),
]
