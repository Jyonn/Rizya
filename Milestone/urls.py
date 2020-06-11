from django.urls import path

from Milestone.views import MilestoneView, IDView, CoverView

urlpatterns = [
    path('', MilestoneView.as_view()),
    path('@<str:mid>', IDView.as_view()),
    path('@<str:mid>/cover', CoverView.as_view()),
]
