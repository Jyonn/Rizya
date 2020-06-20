import datetime
import re

from SmartDjango import models, E
from django.utils.crypto import get_random_string

from Base.qiniu.policy import Policy
from Base.qiniu.qn import qn_res_manager


@E.register(id_processor=E.idp_cls_prefix())
class ResourceError:
    NOT_FOUND = E("资源不存在")
    GRID_POSITION = E("网格坐标格式错误")
    NOT_ALBUM_IMAGE = E("只能删除相册图片")


class Resource(models.Model):
    """资源类 图片或相册"""
    class Meta:
        abstract = True

    res_id = models.CharField(
        max_length=6,
        min_length=6,
        unique=True,
    )

    grid_position = models.CharField(
        max_length=30,
        null=True,
        default=None,
        verbose_name='网格坐标，为(X,Y)的形式'
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    @staticmethod
    def _valid_grid_position(grid_position):
        pattern = r'^\(\d+,\d+\)$'
        if not re.match(pattern, grid_position):
            return ResourceError.GRID_POSITION

    @classmethod
    def get(cls, res_id):
        try:
            return cls.objects.get(res_id=res_id)
        except cls.DoesNotExist:
            raise ResourceError.NOT_FOUND

    def get_grid_position(self):
        if not self.grid_position:
            return

        pattern = r'^\((\d+),(\d+)\)$'
        groups = re.search(pattern, self.grid_position).groups()
        return tuple(map(int, groups))

    @classmethod
    def is_id_unique(cls, res_id):
        try:
            cls.objects.get(res_id=res_id)
            return False
        except cls.DoesNotExist:
            return True

    @classmethod
    def generate_res_id(cls):
        while True:
            res_id = get_random_string(6)
            if cls.is_id_unique(res_id):
                return res_id

    def _readable_grid_position(self):
        return self.get_grid_position()

    def _readable_create_time(self):
        return self.create_time.timestamp()


@E.register(id_processor=E.idp_cls_prefix())
class ImageError:
    NOT_FOUND = E("图片不存在")
    CREATE = E("图片上传失败")
    AS_COVER = E("相册封面无法删除")


class ImageUploadAction:
    MILESTONE = 'milestone'
    ALBUM = 'album'
    SPACEMAN = 'spaceman'
    SPACE = 'space'
    ALBUM_COVER = 'album-cover'


class Image(Resource):
    key = models.CharField(
        max_length=100,
        unique=True,
    )

    width = models.IntegerField()
    height = models.IntegerField()

    color_average = models.CharField(
        max_length=20,
        null=True,
        default=None,
    )

    mime_type = models.CharField(
        max_length=50,
    )

    album = models.ForeignKey(
        'Album.Album',
        on_delete=models.CASCADE,
        null=True,
    )

    orientation = models.IntegerField(
        default=1,
    )

    def get_member(self, user):
        if self.album:
            return self.album.space.get_member(user)
        raise ImageError.NOT_ALBUM_IMAGE

    def not_cover_checker(self):
        if self.album and self.album.cover == self:
            raise ImageError.AS_COVER

    @classmethod
    def orientation_str2int(cls, orientation: list):
        if orientation[0] == 'TOP':
            return 1 if orientation[1] == 'LEFT' else 2
        elif orientation[0] == 'BOTTOM':
            return 4 if orientation[1] == 'LEFT' else 3
        elif orientation[1] == 'TOP':
            return 5 if orientation[1] == 'LEFT' else 6
        else:
            return 8 if orientation[1] == 'LEFT' else 7

    @classmethod
    def orientation_int2str(cls, orientation: int):
        o = orientation - 1
        s = [''] * 2

        s[o // 4] = 'TOP' if orientation in [1, 2, 5, 6] else 'BOTTOM'
        s[1 - o // 4] = 'LEFT' if orientation in [1, 4, 5, 8] else 'RIGHT'
        return '-'.join(s)

    @classmethod
    def get(cls, res_id):
        try:
            return cls.objects.get(res_id=res_id)
        except cls.DoesNotExist:
            return ImageError.NOT_FOUND

    @classmethod
    def create(cls, width, height, orientation, **kwargs):
        if orientation >= 5:
            width, height = height, width

        try:
            return cls.objects.create(
                **kwargs,
                width=width,
                height=height,
                orientation=orientation,
                res_id=cls.generate_res_id(),
                grid_position=None,
            )
        except Exception as err:
            raise ImageError.CREATE(debug_message=err)

    @classmethod
    def get_token(cls, action, **kwargs):
        kwargs.update(dict(action=action))
        key = hex(int(datetime.datetime.now().timestamp() * 1000))
        key = key + '/' + get_random_string(length=16)
        return qn_res_manager.get_upload_token(key=key, policy=Policy.customize(**kwargs))

    @classmethod
    def get_tokens(cls, action, num, **kwargs):
        kwargs.update(dict(action=action))
        key_prefix = hex(int(datetime.datetime.now().timestamp() * 1000))

        tokens = []
        for _ in range(num):
            key = key_prefix + '/' + get_random_string(length=16)
            tokens.append(qn_res_manager.get_upload_token(
                key=key, policy=Policy.customize(**kwargs)))
        return tokens

    def get_source(self, expires=3600, auto_rotate=True, resize=None):
        return qn_res_manager.get_image(
            self.key, expires=expires, auto_rotate=auto_rotate, resize=resize)

    def get_sources(self):
        return dict(
            origin=self.get_source(auto_rotate=False, resize=None),
            square=self.get_source(auto_rotate=True, resize=(200, 200)),
            rotate=self.get_source(auto_rotate=True, resize=None)
        )

    def get_tiny_source_with_color(self, resize=None, with_origin=False):
        d = dict(
            source=self.get_source(auto_rotate=True, resize=resize),
            color=self.color_average,
        )
        if with_origin:
            d["origin"] = self.get_source(auto_rotate=False, resize=None)
        return d

    def delete(self, *args, **kwargs):
        qn_res_manager.delete_res(self.key)
        super(Image, self).delete(*args, **kwargs)

    def _readable_source(self):
        return self.get_tiny_source_with_color(with_origin=True)

    def _readable_orientation(self):
        return [self.orientation, self.orientation_int2str(self.orientation)]

    def d(self):
        d = dict(type='image')
        d.update(self.dictify(
            'source',
            'width',
            'height',
            'res_id',
        ))
        return d

    def d_space(self):
        return self.get_tiny_source_with_color((600, None))

    def d_invite(self):
        return self.get_tiny_source_with_color((600, 480))

    def d_milestone(self):
        return self.get_tiny_source_with_color((400, None))

    def d_avatar(self):
        return self.get_tiny_source_with_color((200, 200))

    def d_base(self):
        return self.dictify('source')


class ImageP:
    image_id, grid_position = Image.get_params('res_id', 'grid_position')
    image_id.rename('image_id', '图片ID')

    id_getter = image_id.clone().rename(
        'image_id', yield_name='image', stay_origin=True).process(Image.get)
