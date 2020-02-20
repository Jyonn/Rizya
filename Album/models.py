from SmartDjango import models, E

from Base.utils import error_add_class_prefix
from Image.models import Resource, Image


@E.register(id_processor=error_add_class_prefix)
class AlbumError:
    CREATE = E("创建相册失败")


class Album(Resource):
    space = models.ForeignKey(
        'Space.Space',
        on_delete=models.CASCADE,
        null=False,
    )

    parent = models.ForeignKey(
        'Album',
        on_delete=models.CASCADE,
        default=None,
        null=True,
    )

    name = models.CharField(
        max_length=20,
        null=True,
    )

    grid_rows = models.IntegerField(
        min_value=4,
        max_value=10,
        default=4,
    )

    auto_arrange = models.BooleanField(
        default=True,
    )

    cover = models.ForeignKey(
        'Image.Image',
        on_delete=models.SET_NULL,
        null=True,
        related_name='cover',
    )

    def born(self, name) -> 'Album':
        try:
            return Album.objects.create(
                space=self.space,
                parent=self,
                name=name,
                grid_rows=4,
                auto_arrange=True,
                cover=None
            )
        except Exception:
            raise AlbumError.CREATE

    def set_cover(self, image):
        self.cover = image
        self.save()

    def d(self):
        return self.dictor(
            'name', 'grid_rows', 'auto_arrange', 'cover', 'res_id->album_id',
            'create_time', 'grid_position')

    def d_layer(self):
        d_ = self.d()
        d_.update(dict(
            albums=Album.objects.filter(parent=self).dict(Album.d),
            images=Image.objects.filter(album=self).dict(Image.d),
        ))
        return d_


class AlbumP:
    name, album_id, grid_position = Album.get_params('name', 'res_id', 'grid_position')
    album_id.rename('album_id', '相册ID')

    id_getter = album_id.clone().rename(
        'album_id', yield_name='album', stay_origin=True).process(Album.get)
