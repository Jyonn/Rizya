from django.urls import path

from Milestone.views import MilestoneView, IDView

urlpatterns = [
    path('', MilestoneView.as_view()),
    path('@<str:mid>', IDView.as_view()),
]
