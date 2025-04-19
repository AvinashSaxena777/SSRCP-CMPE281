from django.db import transaction
from ..models import Robot

class RobotDAO:
    @classmethod
    def get_all_robots(cls, user):
        if user.profile.userType.typeName == 'SUPER_ADMIN':
            return Robot.objects.filter(isActive=True)\
                .select_related('owner__profile__org')\
                .order_by('-created_at')
        elif user.profile.userType.typeName == 'ADMIN':
            return Robot.objects.filter(
                owner__profile__org=user.profile.org,
                isActive=True
            ).select_related('owner__profile__org')
        else:
            return Robot.objects.filter(
                owner=user,
                isActive=True
            ).select_related('owner__profile__org')

    @classmethod
    @transaction.atomic
    def bulk_delete(cls, robot_ids):
        Robot.objects.filter(id__in=robot_ids).update(isActive=False)

    @classmethod
    @transaction.atomic
    def create_robot(cls, data, owner):
        return Robot.objects.create(
            modelName=data['modelName'],
            simulationSession=data.get('simulationSession', 101),
            owner=owner,
            version=data.get('version', 1.0),
            healthStatus=data.get('healthStatus', 100)
        )

    @classmethod
    @transaction.atomic
    def update_robot(cls, robot_id, data):
        robot = Robot.objects.get(id=robot_id)
        robot.robotId = data['robotId']
        robot.cameraTop = data['cameraTop']
        robot.cameraFront = data['cameraFront']
        robot.save()
        return robot
