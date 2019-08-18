from SmartDjango import Packing
from django.views import View

from Message.models import Message


class BaseView(View):
    """ /api/message """
    @staticmethod
    @Packing.http_pack
    def get(r):
        messages = Message.objects.filter(read=False)
        messages_ = messages.dict(Message.d)
        for message in messages:
            message.reading()
        return messages_
