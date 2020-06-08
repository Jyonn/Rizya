from django.urls import path

from Space.views import SpaceView, NameView, MemberView, MemberAvatarView, CoverView

urlpatterns = [
    path('', SpaceView.as_view()),
    path('@<str:space_id>', NameView.as_view()),
    path('@<str:space_id>/cover', CoverView.as_view()),
    path('@<str:space_id>/members', MemberView.as_view()),
    path('@<str:space_id>/member/avatar', MemberAvatarView.as_view()),
]
