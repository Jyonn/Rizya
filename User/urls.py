from django.urls import path

from User import views

urlpatterns = [
    path('', views.UserView.as_view()),
    path('code', views.CodeView.as_view()),
    path('token', views.TokenView.as_view()),
]
