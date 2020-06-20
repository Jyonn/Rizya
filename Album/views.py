from SmartDjango import Analyse
from django.views import View
from smartify import P

from Album.models import Album, AlbumP
from Base.auth import Auth
from Base.common import boundary
from Image.models import ImageP, Image, ImageUploadAction


class IDView(View):
    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter])
    @Auth.require_album_member
    def get(r):
        """获取相册信息"""
        return r.d.album.d_layer()

    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter], b=[AlbumP.name, AlbumP.grid_rows])
    @Auth.require_album_member
    def post(r):
        """新增子相册"""
        album = r.d.album.born(r.d.name)
        return album.get_image_token()

    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter], b=[AlbumP.name, AlbumP.grid_rows])
    @Auth.require_album_member
    def put(r):
        """修改相册"""
        r.d.album.update(**r.d.dict('name', 'grid_rows'))
        return 0

    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter])
    @Auth.require_album_member
    def delete(r):
        """删除相册"""
        album = r.d.album
        album.not_root_checker()
        album.delete()
        return 0


class CoverView(View):
    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter], b=[ImageP.id_getter])
    @Auth.require_album_member
    def put(r):
        album = r.d.album  # type: Album
        image = r.d.image  # type: Image
        album.set_cover(image)
        return 0


class ImageTokenView(View):
    @staticmethod
    @Analyse.r(
        a=[AlbumP.id_getter],
        q=[P('image_num', '图片数量').process(boundary(max_=99, min_=1))]
    )
    @Auth.require_album_member
    def get(r):
        album = r.d.album  # type: Album
        image_num = r.d.image_num

        return Image.get_tokens(
            action=ImageUploadAction.ALBUM,
            num=image_num,
            album_id=album.res_id
        )
