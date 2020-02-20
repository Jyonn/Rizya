from django.urls import path

from Base.views import ErrorView

urlpatterns = [
    path('error', ErrorView.as_view()),
]
