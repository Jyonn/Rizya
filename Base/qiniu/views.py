from SmartDjango import Analyse
from django.views import View

from Album.models import AlbumP
from Base.qiniu.qn import qn_res_manager
from Image.models import ImageUploadAction, Image
from Space.models import SpaceP


class QiniuImageView(View):
    """/base/3-party/qiniu/image"""

    @staticmethod
    @Analyse.r(b=[
        'key', 'action', 'mime_type', 'color_average', 'image_info',
        AlbumP.id_getter.clone().default(),
        SpaceP.spaceman_getter.clone().default(),
    ])
    def post(r):
        qn_res_manager.auth_callback(r)

        action = r.d.action  # type:str
        color_average = r.d.color_average['RGB']  # type: str
        image_info = r.d.image_info

        if 'orientation' in image_info:
            orientation = image_info['orientation'].upper().split('-')
            orientation = Image.orientation_str2int(orientation)
        else:
            orientation = 1
        width, height = image_info['width'], image_info['height']

        album = None
        if action == ImageUploadAction.ALBUM:
            album = r.d.album

        image = Image.create(
            **r.d.dict('key', 'mime_type'),
            color_average=color_average,
            width=width,
            height=height,
            orientation=orientation,
            album=album,
        )

        if action == ImageUploadAction.SPACEMAN:
            spaceman = r.d.spaceman
            spaceman.set_avatar(image)
            return image.d_avatar()

        return image.d()
