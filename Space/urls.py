from django.urls import path

from Space.views import SpaceView, IDView, MemberView, MemberAvatarView, MemberIDView

urlpatterns = [
    path('', SpaceView.as_view()),
    path('@<str:space_id>', IDView.as_view()),
    path('@<str:space_id>/member', MemberView.as_view()),
    path('@<str:space_id>/member/avatar', MemberAvatarView.as_view()),
    path('@<str:space_id>/member/@<str:user_id>', MemberIDView.as_view()),
]
