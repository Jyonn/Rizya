from django.views import View

from Message.models import Message


class BaseView(View):
    """ /api/message """
    @staticmethod
    def get(_):
        messages = Message.objects.filter(read=False)
        messages_ = messages.dict(Message.d)
        for message in messages:
            message.reading()
        return messages_
