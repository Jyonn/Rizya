from django.urls import path

from User.views import UserOAuthView, UserView, UserInviteView

urlpatterns = [
    path('', UserView.as_view()),
    path('oauth', UserOAuthView.as_view()),
    path('invitation', UserInviteView.as_view()),
]
