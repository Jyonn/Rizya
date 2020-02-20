from django.urls import path

from Album.views import AlbumIDView, AlbumCoverView, AlbumImageTokenView

urlpatterns = [
    # path('', AlbumView.as_view()),
    path('@<str:album_id>', AlbumIDView.as_view()),
    path('@<str:album_id>/cover', AlbumCoverView.as_view()),
    path('@<str:album_id>/image-token', AlbumImageTokenView.as_view()),
]
