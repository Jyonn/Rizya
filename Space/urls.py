from django.urls import path

from Space.views import SpaceView, NameView, MemberView, MemberAvatarView

urlpatterns = [
    path('', SpaceView.as_view()),
    path('@<str:name>', NameView.as_view()),
    path('@<str:name>/members', MemberView.as_view()),
    path('@<str:name>/member/avatar', MemberAvatarView.as_view()),
]
