import re

from SmartDjango import models, E, Hc
from smartify import P

from Base.error import error_add_class_prefix


@E.register(id_processor=error_add_class_prefix)
class UserError:
    NOT_FOUND = E("不存在的用户", hc=Hc.NotFound)
    CREATE = E("新建用户错误", hc=Hc.InternalServerError)
    INVALID_USER_ID = E("用户名只能包含字母数字和下划线")


class User(models.Model):
    user_id = models.CharField(
        max_length=16,
        min_length=4,
        unique=True,
        null=True,
    )

    rename_card = models.PositiveSmallIntegerField(
        default=1,
    )

    avatar = models.CharField(
        verbose_name='头像',
        default=None,
        null=True,
        blank=True,
        max_length=1024,
    )

    nickname = models.CharField(
        verbose_name='昵称',
        default=None,
        blank=True,
        null=True,
        max_length=10,
    )

    qt_user_app_id = models.CharField(
        verbose_name='齐天簿ID',
        max_length=16,
    )

    qt_token = models.CharField(
        verbose_name='齐天簿口令',
        max_length=256,
        min_length=4,
    )

    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default=None,
    )

    @staticmethod
    def _valid_user_id(user_id):
        valid_chars = '^[A-Za-z0-9_]+$'
        if re.match(valid_chars, user_id) is None:
            raise UserError.INVALID_USER_ID

    @staticmethod
    def get(user_id):
        try:
            return User.objects.get(user_id__iexist=user_id)
        except User.DoesNotExist:
            raise UserError.NOT_FOUND

    @staticmethod
    def get_by_qt(qt_user_app_id):
        try:
            return User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist as err:
            raise UserError.NOT_FOUND(debug_message=err)

    @classmethod
    def is_user_id_unique(cls, user_id: str):
        try:
            cls.objects.get(user_id__iexist=user_id.lower())
        except cls.DoesNotExist:
            return True
        return False

    @classmethod
    def create(cls, qt_user_app_id, qt_token):
        cls.validator(locals())

        try:
            user = cls.get_by_qt(qt_user_app_id)
            user.qt_token = qt_token
            user.save()
            return user
        except E as e:
            try:
                user = cls.objects.create(
                    user_id=qt_user_app_id,
                    rename_card=1,
                    qt_user_app_id=qt_user_app_id,
                    qt_token=qt_token,
                )
            except Exception as err:
                raise UserError.CREATE(debug_message=err)

    def update(self):
        from Base.common import qt_manager
        data = qt_manager.get_user_info(self.qt_token)
        self.avatar = data['avatar']
        self.nickname = data['nickname']
        self.phone = qt_manager.get_user_phone(self.qt_token)
        self.save()

    def rename(self, user_id: str):
        if self.rename_card < 1:
            raise UserError.REQUIRE_RENAME_CARD

        if not self.is_user_id_unique(user_id):
            raise UserError.NAME_EXIST

        self.user_id = user_id
        self.rename_card -= 1
        self.save()

    def d(self):
        return self.dictor('nickname', 'avatar', 'user_id')


class UserP:
    user_id, nickname = User.get_params('user_id', 'nickname')

    user_getter = user_id.clone().rename(
        'user_id', yield_name='user', stay_origin=True).process(User.get)

    users_getter = P('users', '用户列表').process(list).process(
        lambda users: list(map(User.get, users)))
