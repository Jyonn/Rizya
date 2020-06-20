from typing import Optional

from SmartDjango import Analyse
from django.views import View

from Album.models import AlbumP, Album
from Base.qiniu.qn import qn_res_manager
from Image.models import ImageUploadAction, Image
from Milestone.models import MilestoneP
from Space.models import SpaceP


class QiniuImageView(View):
    """/base/3-party/qiniu/image"""

    @staticmethod
    @Analyse.r(b=[
        'key', 'action', 'mime_type', 'color_average', 'image_info',
        AlbumP.id_getter.clone().default().null(),
        SpaceP.spaceman_getter.clone().default().null(),
        MilestoneP.id_getter.clone().default().null(),
        SpaceP.space_getter.clone().default().null(),
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
        if action in [ImageUploadAction.ALBUM, ImageUploadAction.ALBUM_COVER]:
            album = r.d.album  # type: Optional[Album]

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
            return image.d_base()

        elif action == ImageUploadAction.ALBUM_COVER:
            album.set_cover(image)
            return album.d()

        elif action == ImageUploadAction.MILESTONE:
            milestone = r.d.milestone
            milestone.set_cover(image)
            return image.d_base()

        return image.d()
