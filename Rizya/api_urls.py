from django.urls import path, include

urlpatterns = [
    path('/memory', include('Memory.urls')),
    path('/message', include('Message.urls')),
    path('/trigger', include('Trigger.urls')),
]
