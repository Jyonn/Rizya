from django.urls import path, include

urlpatterns = [
    path('qiniu/', include('Base.qiniu.urls'))
]
