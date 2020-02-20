from SmartDjango import Analyse
from django.views import View

from Base.auth import Auth
from Space.models import SpaceP, Space, SpaceMan
from User.models import UserP


class SpaceView(View):
    @staticmethod
    @Analyse.r(b=[SpaceP.name, SpaceP.access])
    @Auth.require_login
    def post(r):
        return Space.create(**r.d.dict(), user=r.user).d()


class SpaceNameView(View):
    @staticmethod
    @Analyse.r(a=[SpaceP.name_getter])
    def get(r):
        return r.d.space.d()


class SpaceManView(View):
    """/space/members"""

    @staticmethod
    @Analyse.r(a=[SpaceP.name_getter])
    def get(r):
        return r.d.space.spaceman_set.dict(SpaceMan.d_space)

    @staticmethod
    @Analyse.r(a=[SpaceP.name_getter], b=[UserP.users_getter])
    @Auth.require_login
    def put(r):
        """空间新增用户（邀请）"""
        space = r.d.space
        space.owner_checker(r.user)
        space.invite(r.d.users)

    @staticmethod
    @Analyse.r(a=[SpaceP.name_getter], b=['accept'])
    @Auth.require_login
    def post(r):
        """接受或拒绝邀请"""
        space_man = r.d.space.get_man(r.user)  # type: SpaceMan
        space_man.accept(r.d.accept)

    @staticmethod
    @Analyse.r(a=[SpaceP.name_getter], b=[UserP.users_getter])
    @Auth.require_login
    def patch(r):
        """空间删除用户"""
        space = r.d.space
        space.owner_checker(r.user)
        space.remove_man(r.d.users)
