from SmartDjango import Analyse
from django.views import View
from smartify import P

from Album.models import Album, AlbumP
from Base.common import boundary
from Image.models import ImageP, Image, ImageUploadAction
from Space.models import SpaceP, Space

#
# class AlbumView(View):
#     @staticmethod
#     @Analyse.r(a=[SpaceP.name_getter])
#     def get(r):
#         space = r.d.space  # type: Space
#         album = space.get_album()
#         return album.d()


class IDView(View):
    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter])
    def get(r):
        """获取相册信息"""
        return r.d.album.d_layer()

    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter], b=[AlbumP.name])
    def post(r):
        """新增子相册"""
        return r.d.album.born(r.d.name).d()

    # @staticmethod
    # @Analyse.r(a=[AlbumP.id_getter], b=[AlbumP.name])
    # def put(r):


class CoverView(View):
    @staticmethod
    @Analyse.r(a=[AlbumP.id_getter], b=[ImageP.id_getter])
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
    def get(r):
        album = r.d.album  # type: Album
        image_num = r.d.image_num

        return Image.get_tokens(
            action=ImageUploadAction.ALBUM,
            num=image_num,
            album_id=album.res_id
        )
