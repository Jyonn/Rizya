from django.urls import path

from Image.views import IDView

urlpatterns = [
    path('@<str:image_id>', IDView.as_view()),
]
