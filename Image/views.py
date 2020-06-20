from SmartDjango import Analyse
from django.views import View

from Base.auth import Auth
from Image.models import ImageP


class IDView(View):
    @staticmethod
    @Analyse.r(a=[ImageP.id_getter])
    @Auth.require_image_member
    def delete(r):
        image = r.d.image
        image.not_cover_checker()
        image.delete()
        return 0
