import re
import string

from SmartDjango import models, E
from django.db import transaction
from django.utils.crypto import get_random_string
from smartify import P

from Album.models import Album
from Image.models import Image, ImageUploadAction
from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class SpaceError:
    INVALID_ID_SIDE = E("星球ID首尾字符只能是字母或数字")
    INVALID_ID = E("星球ID只能包含字母数字和中下划线")
    ID_EXIST = E("星球ID已存在")
    CREATE = E("创建星球{0}失败")
    REMOVE_MAN = E("移除居民失败")
    NOT_FOUND = E("空间不存在")
    REQUIRE_RENAME_CARD = E("空间改名卡不足")
    NOT_OWNER = E("不是星球球主，无法操作")
    NOT_MEMBER = E("不是星球居民，无法操作")
    MEMBER_NOT_FOUND = E("居民不存在")


class AccessChoices(models.CEnum):
    ANY = 'any'
    USR = 'user'
    PRV = 'privacy'


class Space(models.Model):
    space_id = models.CharField(
        max_length=20,
        min_length=4,
        unique=True,
        verbose_name='星球ID',
        null=False,
    )

    name = models.CharField(
        max_length=15,
        min_length=2,
        verbose_name='星球名',
        default=None,
        null=True,
    )

    rename_card = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='星球改ID卡',
    )

    access = models.CharField(
        choices=AccessChoices.list(),
        default=AccessChoices.ANY,
        max_length=10,
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    default_milestone = models.ForeignKey(
        'Milestone.Milestone',
        default=None,
        null=True,
        on_delete=models.SET_NULL,
        related_name='default_milestone'
    )

    # cover = models.ForeignKey(
    #     'Image.Image',
    #     default=None,
    #     null=True,
    #     on_delete=models.SET_NULL,
    # )

    @staticmethod
    def _valid_space_id(space_id):
        if space_id[0] not in string.ascii_lowercase + string.ascii_uppercase + string.digits:
            raise SpaceError.INVALID_ID_SIDE
        if space_id[-1] not in string.ascii_lowercase + string.ascii_uppercase + string.digits:
            raise SpaceError.INVALID_ID_SIDE
        valid_chars = '^[A-Za-z0-9_-]+$'
        if re.match(valid_chars, space_id) is None:
            raise SpaceError.INVALID_ID

    @classmethod
    def get_unique_id(cls):
        while True:
            space_id = get_random_string(length=8)
            try:
                cls.id_unique_checker(space_id)
                return space_id
            except E:
                pass

    # checkers

    @classmethod
    def id_unique_checker(cls, space_id: str):
        try:
            cls.objects.get(space_id__iexact=space_id.lower())
        except cls.DoesNotExist:
            return
        raise SpaceError.ID_EXIST

    def owner_checker(self, user):
        if self.spaceman_set.get(is_owner=True).user != user:
            raise SpaceError.NOT_OWNER

    def member_checker(self, user):
        try:
            self.spaceman_set.get(user=user)
        except Exception:
            raise SpaceError.NOT_MEMBER

    # classmethods

    @classmethod
    def get(cls, space_id: str):
        try:
            return cls.objects.get(space_id__iexact=space_id.lower())
        except cls.DoesNotExist:
            raise SpaceError.NOT_FOUND

    @classmethod
    def create(cls, name, access, start_date, user):
        from Milestone.models import Milestone

        try:
            with transaction.atomic():
                space = cls.objects.create(
                    space_id=cls.get_unique_id(),
                    rename_card=0,
                    access=access,
                    name=name,
                )
                space.spaceman_set.create(
                    user=user,
                    avatar=None,
                    name=user.nickname,
                    is_owner=True,
                )
                space.album_set.create(
                    parent=None,
                    name=None,
                    grid_rows=4,
                    grid_position=None,
                    auto_arrange=True,
                    cover=None,
                    res_id=Album.generate_res_id(),
                )
                milestone = Milestone.create(
                    space=space,
                    name='星球成立日',
                    start_date=start_date
                )
                space.set_default_milestone(milestone)
        except Exception as err:
            raise SpaceError.CREATE(name, debug_message=err)
        return space

    def delete(self, *args, **kwargs):
        super(Space, self).delete(*args, **kwargs)

    def rename(self, space_id: str):
        if self.rename_card < 1:
            raise SpaceError.REQUIRE_RENAME_CARD
        self.id_unique_checker(space_id)

        self.space_id = space_id
        self.rename_card -= 1
        self.save()

    # member

    def get_member(self, user):
        try:
            return self.spaceman_set.get(user=user)
        except Exception:
            raise SpaceError.MEMBER_NOT_FOUND

    def remove_member(self, users):
        try:
            with transaction.atomic():
                for user in users:
                    self.get_member(user).delete()
        except Exception as err:
            raise SpaceError.REMOVE_MAN(debug_message=err)

    # cover

    def get_cover_token(self):
        return self.default_milestone.get_image_token()

    def get_album(self):
        return self.album_set.get(parent=None)

    def set_default_milestone(self, milestone):
        self.default_milestone = milestone
        self.save()

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_owner(self):
        return self.spaceman_set.get(is_owner=True).user.d()

    def _readable_root_album(self):
        return self.get_album().res_id

    def _readable_cover(self):
        if self.default_milestone.cover:
            return self.default_milestone.cover.d_space()

    def _readable_members(self, only_avatar=True):
        if only_avatar:
            return self.spaceman_set.dict(SpaceMan.get_avatar)
        return self.spaceman_set.dict(SpaceMan.d_space)

    def _readable_age(self):
        return self.default_milestone.get_duration()

    def _readable_milestones(self):
        from Milestone.models import Milestone
        return self.milestone_set.dict(Milestone.d)

    def d(self):
        return self.dictify('name', 'access', 'owner', 'root_album', 'age', 'milestones')

    def d_create(self):
        return dict(
            space_dict=self.space_id,
            cover_token=self.get_cover_token(),
        )

    def d_base(self):
        return self.dictify('name', 'access', 'space_id', 'cover', 'members', 'age')

    def d_member(self):
        return self._readable_members(only_avatar=False)


class SpaceMan(models.Model):
    class Meta:
        unique_together = ('user', 'space')

    user = models.ForeignKey(
        'User.User',
        on_delete=models.CASCADE,
    )

    avatar = models.ForeignKey(
        'Image.Image',
        on_delete=models.SET_NULL,
        null=True,
    )

    name = models.CharField(
        verbose_name='名字',
        max_length=20,
    )

    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
    )

    is_owner = models.BooleanField(
        default=False,
    )

    @classmethod
    def get_by_union(cls, space_user_union: str):
        space_name, user_id = space_user_union.rsplit('-', 1)
        space = Space.get(space_name)
        user = User.get(user_id)
        return space.get_member(user)

    def get_union(self):
        return '-'.join([self.space.space_id, self.user.user_id])

    def delete(self, *args, **kwargs):
        if self.avatar:
            self.avatar.delete()
        super(SpaceMan, self).delete(*args, **kwargs)

    # 星球居民头像

    def set_avatar(self, image):
        if self.avatar:
            self.avatar.delete()
        self.avatar = image
        self.save()

    def get_avatar_token(self):
        return Image.get_token(
            action=ImageUploadAction.SPACEMAN,
            space_user=self.get_union(),
        )

    def get_avatar(self):
        if self.avatar:
            return self.avatar.get_source(auto_rotate=True, resize=(200, 200))
        return self.user.avatar

    def _readable_user(self):
        return self.user.d()

    def _readable_space(self):
        return self.space.d()

    def _readable_avatar(self):
        return self.get_avatar()

    def d_space(self):
        return self.dictify('user', 'avatar', 'name', 'is_owner')

    def d_user(self):
        return self.dictify('avatar', 'name', 'is_owner', 'space')

    def d_user_base(self):
        return self.space.d_base()


class SpaceP:
    space_id, name, rename_card, access = Space.P('space_id', 'name', 'rename_card', 'access')

    space_getter = space_id.clone().rename(
        'space_id', yield_name='space', stay_origin=True).process(Space.get)

    spaceman_getter = P('space_user', yield_name='spaceman').process(SpaceMan.get_by_union)
