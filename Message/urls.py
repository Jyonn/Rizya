from django.urls import path

from Message.views import BaseView

urlpatterns = [
    path('', BaseView.as_view()),
]
