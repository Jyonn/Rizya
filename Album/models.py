from SmartDjango import models, E

from Image.models import Resource, Image


@E.register(id_processor=E.idp_cls_prefix())
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
                grid_rows=6,
                auto_arrange=True,
                cover=None,
                res_id=self.generate_res_id(),
                grid_position=None,
            )
        except Exception:
            raise AlbumError.CREATE

    def delete(self, *args, **kwargs):
        if self.cover:
            self.cover.delete()
        super().delete(*args, **kwargs)

    def set_cover(self, image):
        self.cover = image
        self.save()

    def d(self):
        d = dict(type='album')
        d.update(self.dictify(
            'name',
            'grid_rows',
            # 'auto_arrange',
            # 'cover',
            'res_id',
            # 'create_time',
            # 'grid_position'
        ))
        return d

    def d_layer(self):
        d = self.d()
        d.update(dict(
            albums=self.album_set.dict(Album.d),
            images=self.image_set.dict(Image.d),
        ))
        return d

    def d_image(self):
        return self.cover.d()


class AlbumP:
    name, album_id, grid_position = Album.get_params('name', 'res_id', 'grid_position')
    album_id.rename('album_id', '相册ID')

    id_getter = album_id.clone().rename(
        'album_id', yield_name='album', stay_origin=True).process(Album.get)

    auto_arrange, grid_rows = Album.get_params('auto_arrange', 'grid_rows')
