from SmartDjango import Analyse
from django.http import HttpRequest
from django.views import View
from smartify import P

from Album.models import AlbumP, Album
from Base.qiniu.qn import qn_res_manager
from Image.models import ImageUploadAction


class QiniuImageView(View):
    """/base/3-party/qiniu/image"""

    @staticmethod
    @Analyse.r(b=[
        'key', 'action', 'mime_type', 'color_average', 'image_info',
        AlbumP.id_getter.clone().default()])
    def post(r):
        qn_res_manager.auth_callback(r)

        action = r.d.aciton

        # if action == ImageUploadAction.ALBUM:
        #     album = r.d.album  # type: Album
        #     album.
        print(r.d.dict())

        return 1