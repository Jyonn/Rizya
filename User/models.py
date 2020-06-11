from SmartDjango import models, E, Hc
from django.utils.crypto import get_random_string
from smartify import P


@E.register(id_processor=E.idp_cls_prefix())
class UserError:
    NOT_FOUND = E("不存在的用户", hc=Hc.NotFound)
    CREATE = E("新建用户错误", hc=Hc.InternalServerError)


class User(models.Model):
    user_id = models.CharField(
        max_length=16,
        min_length=4,
        unique=True,
        null=True,
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
        max_length=64,
    )

    openid = models.CharField(
        max_length=64,
        unique=True,
    )

    @classmethod
    def get_unique_id(cls):
        while True:
            user_id = get_random_string(length=6)
            try:
                cls.get(user_id)
            except E:
                return user_id

    @classmethod
    def get(cls, user_id):
        try:
            return cls.objects.get(user_id=user_id)
        except cls.DoesNotExist:
            raise UserError.NOT_FOUND

    @classmethod
    def get_or_create(cls, openid):
        try:
            return cls.objects.get(openid=openid)
        except cls.DoesNotExist:
            pass

        try:
            return cls.objects.create(
                openid=openid,
                user_id=cls.get_unique_id(),
            )
        except Exception as err:
            raise UserError.CREATE(debug_message=err)

    def update(self, avatar, nickname):
        self.validator(locals())
        self.avatar = avatar
        self.nickname = nickname
        self.save()

    def d(self):
        return self.dictify('nickname', 'avatar', 'user_id')


class UserP:
    user_id, nickname = User.get_params('user_id', 'nickname')

    user_getter = user_id.clone().rename(
        'user_id', yield_name='user', stay_origin=True).process(User.get)
