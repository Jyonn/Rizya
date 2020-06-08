from SmartDjango import Analyse
from django.views import View

from Base.auth import Auth
from Milestone.models import MilestoneP
from Space.models import SpaceP, Space, SpaceMan
from User.models import UserP, User


class SpaceView(View):
    """/space"""

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


class NameView(View):
    """/space/:space_id"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    def get(r):
        """获取空间信息"""
        return r.d.space.d()


class MemberView(View):
    """/space/members"""

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    def get(r):
        """获取空间用户信息"""
        return r.d.space.spaceman_set.dict(SpaceMan.d_space)

    # @staticmethod
    # @Analyse.r(a=[SpaceP.space_getter], b=[UserP.users_getter])
    # @Auth.require_owner
    # def put(r):
    #     """空间新增用户（邀请）"""
    #     space = r.d.space
    #     space.invite(r.d.users)

    # @staticmethod
    # @Analyse.r(a=[SpaceP.space_getter], b=['accept'])
    # @Auth.require_login
    # def post(r):
    #     """接受或拒绝邀请"""
    #     space_man = r.d.space.get_member(r.user)  # type: SpaceMan
    #     space_man.accept(r.d.accept)

    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter], b=[UserP.users_getter])
    @Auth.require_owner
    def patch(r):
        """空间删除用户"""
        space = r.d.space
        space.remove_member(r.d.users)


class MemberAvatarView(View):
    """/space/member/avatar"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_member
    def get(r):
        return r.spaceman.get_avatar_token()


class CoverView(View):
    """/space/:space_id/cover"""
    @staticmethod
    @Analyse.r(a=[SpaceP.space_getter])
    @Auth.require_member
    def get(r):
        return r.d.space.get_cover_token()
