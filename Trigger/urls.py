from django.urls import path

from Trigger.views import BaseView, HubView, IdView, HubIdView

urlpatterns = [
    path('', BaseView.as_view()),
    path('/@<trigger_id: int>', IdView.as_view()),
    path('/hub', HubView.as_view()),
    path('/hub/@<trigger_hub_id: int>', HubIdView.as_view()),
]
