from SmartDjango import models, E, Hc


@E.register()
class ConfigError:
    CREATE_CONFIG = E("更新配置错误", hc=Hc.InternalServerError)
    CONFIG_NOT_FOUND = E("不存在的配置", hc=Hc.NotFound)


class Config(models.Model):
    MAX_L = {
        'key': 100,
        'value': 255,
    }

    key = models.CharField(
        max_length=MAX_L['key'],
        unique=True,
    )

    value = models.CharField(
        max_length=MAX_L['value'],
    )

    @classmethod
    def get_config_by_key(cls, key):
        cls.validator(locals())

        try:
            return cls.objects.get(key=key)
        except cls.DoesNotExist as err:
            raise ConfigError.CONFIG_NOT_FOUND(debug_message=err)

    @classmethod
    def get_value_by_key(cls, key, default=None):
        try:
            return cls.get_config_by_key(key).value
        except Exception:
            return default

    @classmethod
    def update_value(cls, key, value):
        cls.validator(locals())

        try:
            config = cls.get_config_by_key(key)
            config.value = value
            config.save()
        except E as e:
            if e.eid(ConfigError.CONFIG_NOT_FOUND):
                try:
                    config = cls(
                        key=key,
                        value=value,
                    )
                    config.save()
                except Exception as err:
                    raise ConfigError.CREATE_CONFIG(debug_message=err)
            else:
                raise e
        except Exception as err:
            ConfigError.CREATE_CONFIG(debug_message=err)


class ConfigInstance:
    JWT_ENCODE_ALGO = 'jwt-encode-algo'
    PROJECT_SECRET_KEY = 'project-secret-key'

    HOST = 'host'
    QITIAN_APP_ID = 'qt-app-id'
    QITIAN_APP_SECRET = 'qt-app-secret'


CI = ConfigInstance
