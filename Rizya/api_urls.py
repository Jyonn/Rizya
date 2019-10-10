from SmartDjango import Analyse
from django.urls import path, include


@Analyse.r(q=['hi'], a=['text'])
def version(r):
    return r.get_host(), r.d.dict()


urlpatterns = [
    path('/memory', include('Memory.urls')),
    path('/message', include('Message.urls')),
    path('/trigger', include('Trigger.urls')),
    path('/version/<text>', version),
]
