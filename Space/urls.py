from django.urls import path

from Space.views import SpaceView, SpaceNameView, SpaceManView

urlpatterns = [
    path('', SpaceView.as_view()),
    path('@<str:name>', SpaceNameView.as_view()),
    path('@<str:name>/members', SpaceManView.as_view()),
]
