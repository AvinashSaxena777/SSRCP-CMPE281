from django.db import transaction
from ..models import Schedule

class ScheduleDAO:
    @classmethod
    @transaction.atomic
    def create_schedule(cls, data):
        return Schedule.objects.create(
            robot=data['robot'],
            start_latitude=data['start_latitude'],
            start_longitude=data['start_longitude'],
            dest_latitude=data['dest_latitude'],
            dest_longitude=data['dest_longitude'],
            scheduled_at=data['scheduled_at'],
            owner=data['owner']
        )

    @classmethod
    def get_schedule(cls, schedule_id):
        return Schedule.objects.get(id=schedule_id)

    @classmethod
    def get_schedules_by_robot(cls, robot_id):
        return Schedule.objects.filter(robot__id=robot_id).order_by('-scheduled_at')

    @classmethod
    def get_schedules_by_owner(cls, owner_id):
        return Schedule.objects.filter(owner__id=owner_id).order_by('-scheduled_at')

    @classmethod
    @transaction.atomic
    def update_schedule(cls, schedule_id, data):
        schedule = Schedule.objects.get(id=schedule_id)
        for field, value in data.items():
            setattr(schedule, field, value)
        schedule.save()
        return schedule

    @classmethod
    @transaction.atomic
    def delete_schedule(cls, schedule_id):
        schedule = Schedule.objects.get(id=schedule_id)
        schedule.delete()
        return True

    @classmethod
    @transaction.atomic
    def bulk_delete(cls, schedule_ids):
        Schedule.objects.filter(id__in=schedule_ids).delete()
        return True

    @classmethod
    def get_all_schedules(cls):
        return Schedule.objects.all().order_by('-scheduled_at')
