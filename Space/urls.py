from django.urls import path

from Space.views import SpaceView, IDView, MemberView, MemberAvatarView

urlpatterns = [
    path('', SpaceView.as_view()),
    path('@<str:space_id>', IDView.as_view()),
    path('@<str:space_id>/members', MemberView.as_view()),
    path('@<str:space_id>/member/avatar', MemberAvatarView.as_view()),
]
