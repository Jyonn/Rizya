from SmartDjango import models, E, Hc


@E.register()
class UserError:
    USER_NOT_FOUND = E("不存在的用户", hc=Hc.NotFound)
    CREATE_USER = E("新建用户错误", hc=Hc.InternalServerError)


class User(models.Model):
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

    @staticmethod
    def get_by_qt_user_app_id(qt_user_app_id):
        try:
            return User.objects.get(qt_user_app_id=qt_user_app_id)
        except User.DoesNotExist as err:
            raise UserError.USER_NOT_FOUND(debug_message=err)

    @classmethod
    def create(cls, qt_user_app_id, qt_token):
        cls.validator(locals())

        try:
            user = cls.get_by_qt_user_app_id(qt_user_app_id)
            user.qt_token = qt_token
            user.save()
            return user
        except E as e:
            if e.eis(UserError.USER_NOT_FOUND):
                try:
                    user = cls(
                        qt_user_app_id=qt_user_app_id,
                        qt_token=qt_token,
                    )
                    user.save()
                except Exception as err:
                    raise UserError.CREATE_USER(debug_message=err)
            else:
                raise e
        except Exception as err:
            raise UserError.CREATE_USER(debug_message=err)

    def update(self):
        from Base.common import qt_manager
        data = qt_manager.get_user_info(self.qt_token)
        self.avatar = data['avatar']
        self.nickname = data['nickname']
        self.save()

    def _readable_user_id(self):
        return self.qt_user_app_id

    def d(self):
        return self.dictor('nickname', 'avatar', 'user_id')
