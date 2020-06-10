from functools import wraps

from SmartDjango import E, Hc

from Base.common import DEV_MODE
from Base.crypto import Crypto
from Base.jtoken import JWT
from Space.models import SpaceMan
from User.models import User


@E.register(id_processor=E.idp_cls_prefix())
class AuthError:
    REQUIRE_LOGIN = E("需要登录", hc=Hc.Unauthorized)
    TOKEN_MISS_PARAM = E("认证口令缺少参数{0}", hc=Hc.Forbidden)


class AuthType:
    LOGIN = 'login'
    INVITE = 'invite'


class Auth:
    @staticmethod
    def validate_token(request):
        jwt_str = request.META.get('HTTP_TOKEN')
        if not jwt_str:
            raise AuthError.REQUIRE_LOGIN

        return JWT.decrypt(jwt_str)

    @staticmethod
    def get_login_token(user: User, session_key):
        if DEV_MODE:
            encrypt_session_key = session_key
        else:
            encrypt_session_key = Crypto.AES.encrypt(session_key)
        token, d = JWT.encrypt(dict(
            type=AuthType.LOGIN,
            user_id=user.user_id,
            session_key=encrypt_session_key,
        ))
        d['token'] = token
        d['user'] = user.d()
        return d

    @staticmethod
    def get_invite_token(spaceman: SpaceMan):
        token, d = JWT.encrypt(dict(
            type=AuthType.INVITE,
            spaceman=spaceman.get_union(),
        ))
        d['token'] = token
        d['spaceman'] = spaceman.d_user()
        return d

    @classmethod
    def _extract_user(cls, r):
        r.user = None

        dict_ = cls.validate_token(r)
        user_id = dict_.get('user_id')
        if not user_id:
            raise AuthError.TOKEN_MISS_PARAM('user_id')
        session_key = dict_.get("session_key")
        if not session_key:
            raise AuthError.TOKEN_MISS_PARAM('session_key')
        type_ = dict_.get('type')
        if type_ != AuthType.LOGIN:
            raise AuthError.TOKEN_MISS_PARAM('type')

        if DEV_MODE:
            r.session_key = session_key
        else:
            r.session_key = Crypto.AES.decrypt(session_key)
        r.user = User.get(user_id)

    @classmethod
    def require_login(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            return func(r, *args, **kwargs)
        return wrapper

    @classmethod
    def require_space_owner(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            r.spaceman = r.d.space.get_member(r.user)
            r.d.space.owner_checker(r.user)
            return func(r, *args, **kwargs)
        return wrapper

    @classmethod
    def require_space_member(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            r.spaceman = r.d.space.get_member(r.user)
            return func(r, *args, **kwargs)

        return wrapper

    @classmethod
    def require_milestone_member(cls, func):
        @wraps(func)
        def wrapper(r, *args, **kwargs):
            cls._extract_user(r)
            r.spaceman = r.d.milestone.space.get_member(r.user)
            return func(r, *args, **kwargs)

        return wrapper
