import re
import string

from SmartDjango import models, E
from django.db import transaction
from smartify import P

from Album.models import Album
from Image.models import Image, ImageUploadAction
from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class SpaceError:
    INVALID_NAME_SIDE = E("空间名首尾字符只能是字母")
    INVALID_NAME = E("空间名只能包含字母数字和中下划线")
    NAME_EXIST = E("空间名已存在")
    CREATE = E("创建空间{0}失败")
    INVITE = E("邀请用户失败")
    REMOVE_MAN = E("移除成员失败")
    NOT_FOUND = E("空间不存在")
    REQUIRE_RENAME_CARD = E("空间改名卡不足")
    NOT_OWNER = E("不是空间管理员，无法操作")
    MEMBER_NOT_FOUND = E("成员不存在")


class AccessChoices(models.CEnum):
    ANY = 'any'
    USR = 'user'
    PRV = 'privacy'


class Space(models.Model):
    name = models.CharField(
        max_length=20,
        min_length=4,
        unique=True,
        verbose_name='空间名',
        null=False,
    )

    rename_card = models.PositiveSmallIntegerField(
        default=1,
        verbose_name='空间改名卡',
    )

    access = models.CharField(
        choices=AccessChoices.list(),
        default=AccessChoices.ANY,
        max_length=10,
    )

    create_time = models.DateTimeField(
        auto_now_add=True,
    )

    @staticmethod
    def _valid_name(name):
        if name[0] not in string.ascii_lowercase + string.ascii_uppercase:
            raise SpaceError.INVALID_NAME_SIDE
        if name[-1] not in string.ascii_lowercase + string.ascii_uppercase:
            raise SpaceError.INVALID_NAME_SIDE
        valid_chars = '^[A-Za-z0-9_-]+$'
        if re.match(valid_chars, name) is None:
            raise SpaceError.INVALID_NAME

    @classmethod
    def is_name_unique(cls, name: str):
        try:
            cls.objects.get(name__iexact=name.lower())
        except cls.DoesNotExist:
            return True
        return False

    @classmethod
    def get(cls, name: str):
        try:
            return cls.objects.get(name__iexact=name.lower())
        except cls.DoesNotExist:
            raise SpaceError.NOT_FOUND

    @classmethod
    def create(cls, name: str, access: str, user):
        if not cls.is_name_unique(name):
            raise SpaceError.NAME_EXIST

        try:
            with transaction.atomic():
                space = cls.objects.create(
                    name=name,
                    rename_card=0,
                    access=access,
                )
                space.spaceman_set.create(
                    user=user,
                    avatar=None,
                    name=user.nickname,
                    is_owner=True,
                    accept_invite=True,
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
        except Exception as err:
            raise SpaceError.CREATE(name, debug_message=err)
        return space

    def rename(self, name: str):
        if self.rename_card < 1:
            raise SpaceError.REQUIRE_RENAME_CARD

        if not self.is_name_unique(name):
            raise SpaceError.NAME_EXIST

        self.name = name
        self.rename_card -= 1
        self.save()

    def invite(self, users):
        try:
            with transaction.atomic():
                for user in users:
                    self.spaceman_set.create(
                        user=user,
                        avatar=None,
                        name=user.nickname,
                        is_owner=False,
                        accept_invite=False,
                    )
        except Exception as err:
            raise SpaceError.INVITE(debug_message=err)

    def remove_man(self, users):
        try:
            with transaction.atomic():
                for user in users:
                    self.get_man(user).remove()
        except Exception as err:
            raise SpaceError.REMOVE_MAN(debug_message=err)

    def owner_checker(self, user):
        if self.spaceman_set.get(is_owner=True).user != user:
            raise SpaceError.NOT_OWNER

    def is_owner(self, user):
        try:
            self.owner_checker(user)
            return True
        except E:
            return False

    def get_man(self, user):
        try:
            return self.spaceman_set.get(user=user)
        except Exception:
            raise SpaceError.MEMBER_NOT_FOUND

    def get_album(self):
        return self.album_set.get(parent=None)

    def _readable_create_time(self):
        return self.create_time.timestamp()

    def _readable_owner(self):
        return self.spaceman_set.get(is_owner=True).user.d()

    def _readable_root_album(self):
        return self.get_album().res_id

    def d(self):
        return self.dictor('name', 'access', 'owner', 'root_album')

    def d_member(self):
        return self.spaceman_set.dict(SpaceMan.d_space)


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

    accept_invite = models.BooleanField(
        default=True,
    )

    @classmethod
    def get_by_union(cls, space_user_union: str):
        space_name, user_id = space_user_union.rsplit('-', 1)
        space = Space.get(space_name)
        user = User.get(user_id)
        return space.get_man(user)

    def get_union(self):
        return '-'.join([self.space.name, self.user.user_id])

    def set_avatar(self, image):
        if self.avatar:
            self.avatar.remove()
        self.avatar = image
        self.save()

    def _readable_user(self):
        return self.user.d()

    def _readable_space(self):
        return self.space.d()

    def _readable_avatar(self):
        if self.avatar:
            return self.avatar.get_sources()
        return None

    def d_space(self):
        return self.dictify('user', 'avatar', 'name', 'is_owner', 'accept_invite')

    def d_user(self):
        return self.dictify('avatar', 'name', 'is_owner', 'accept_invite', 'space')

    def accept(self, accept):
        if self.accept_invite:
            return

        if accept:
            self.accept_invite = True
            self.save()
        else:
            self.remove()

    def remove(self):
        self.delete()

    def get_image_token(self):
        return Image.get_token(
            action=ImageUploadAction.SPACEMAN,
            space_user=self.get_union(),
        )


class SpaceP:
    name, rename_card, access = Space.P('name', 'rename_card', 'access')

    name_getter = name.clone().rename(
        'name', yield_name='space', stay_origin=True).process(Space.get)

    spaceman_getter = P('space_user', 'spaceman').process(SpaceMan.get_by_union)
