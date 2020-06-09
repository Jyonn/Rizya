from django.urls import path

from Album.views import IDView, CoverView, ImageTokenView

urlpatterns = [
    # path('', AlbumView.as_view()),
    path('@<str:album_id>', IDView.as_view()),
    path('@<str:album_id>/cover', CoverView.as_view()),
    path('@<str:album_id>/image-token', ImageTokenView.as_view()),
]
