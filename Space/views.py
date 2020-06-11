from SmartDjango import Analyse
from django.views import View
from smartify import P

from Base.auth import Auth
from Milestone.models import MilestoneP
from Space.models import SpaceP, Space, SpaceMan, SpaceManP
from User.models import UserP, User


class SpaceView(View):
    """/space/"""

    @staticmethod
    @Auth.require_login
    def get(r):
        """获取我的空间"""
        user = r.user  # type: User
        return user.spaceman_set.dict(SpaceMan.d_user_base)

    @staticmethod
    @Analyse.r(b=[SpaceP.name, SpaceP.access, MilestoneP.start_date])
    @Auth.require_login
    def post(r):
        """新建空间"""
        return Space.create(**r.d.dict(), user=r.user).d_create()


class IDView(View):
    """/space/:space_id"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_space_member
    def get(r):
        """获取空间信息"""
        d = r.d.space.d()
        d['user'] = r.spaceman.d_space()
        return d

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter, SpaceP.name])
    @Auth.require_space_owner
    def put(r):
        pass

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_space_owner
    def delete(r):
        r.d.space.delete()
        return 0


class MemberView(View):
    """/space/:space_id/member"""

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    def get(r):
        """获取空间用户信息"""
        return r.d.space.spaceman_set.dict(SpaceMan.d_space)

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter], b=[SpaceManP.name])
    @Auth.require_space_member
    def put(r):
        r.spaceman.update(r.d.name)
        return 0


class TicketView(View):
    """/space/:space_id/ticket"""

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_space_member
    def get(r):
        """生成邀请"""
        return Auth.get_invite_ticket(r.spaceman)

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter], b=[
        P('ticket', yield_name='spaceman').process(Auth.analyse_invite_ticket)])
    @Auth.require_login
    def post(r):
        """获取邀请信息"""
        return r.d.spaceman.d_invite()


class MemberAvatarView(View):
    """/space/:space_id/member/avatar"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_space_member
    def get(r):
        return r.spaceman.get_avatar_token()


class MemberIDView(View):
    """/space/:space_id/member/:user_id"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter, UserP.user_getter])
    @Auth.require_space_owner
    def delete(r):
        space = r.d.space
        space_man = space.get_member(r.d.user)  # type: SpaceMan
        space_man.not_owner_checker()
        space_man.delete()
        return 0