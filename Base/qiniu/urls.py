from django.urls import path

from Base.qiniu.views import QiniuImageView

urlpatterns = [
    path('image', QiniuImageView.as_view()),
]
