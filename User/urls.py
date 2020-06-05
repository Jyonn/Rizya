from django.urls import path

from User.views import UserView, CodeView

urlpatterns = [
    path('', UserView.as_view()),
    path('code', CodeView.as_view()),
]
