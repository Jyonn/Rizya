from SmartDjango import Analyse
from django.views import View

from Base.auth import Auth
from Milestone.models import MilestoneP, Milestone
from Space.models import SpaceP


class MilestoneView(View):
    @staticmethod
    @Analyse.r(b=[SpaceP.space_getter, MilestoneP.name, MilestoneP.start_date])
    @Auth.require_space_member
    def post(r):
        return Milestone.create(**r.d.dict()).d_create()


class IDView(View):
    @staticmethod
    @Analyse.r(a=[MilestoneP.id_getter], b=[MilestoneP.name, MilestoneP.start_date])
    @Auth.require_milestone_member
    def put(r):
        milestone = r.d.milestone
        milestone.update(**r.d.dict('name', 'start_date'))
        return 0

    @staticmethod
    @Analyse.r(a=[MilestoneP.id_getter])
    @Auth.require_milestone_member
    def delete(r):
        r.d.milestone.delete()
        return 0
