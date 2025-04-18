from django.db.models import Count
from ..models import Organization, UserProfile, Robot, Alert
from datetime import datetime, timedelta
import random

# Metrics DAOs
def get_organization_count():
    return Organization.objects.filter(isActive=True).count()

def get_user_count():
    return UserProfile.objects.filter(isActive=True).count()

def get_robot_count():
    return Robot.objects.filter(isActive=True).count()

def get_alert_count():
    return Alert.objects.count()

# Chart Data DAOs
def get_organization_distribution(dummy_data=False):
    if dummy_data:
        return {
            'labels': [f'Org {i+1}' for i in range(10)],
            'data': [random.randint(50, 200) for _ in range(10)]
        }
    # Corrected annotation
    orgs = Organization.objects.annotate(
        user_count=Count('userprofile')  # Changed from 'users' to 'userprofile'
    ).order_by('-user_count')[:10]
    
    return {
        'labels': [org.organizationName for org in orgs],
        'data': [org.user_count for org in orgs]
    }


def get_robot_ownership_distribution(dummy_data=False):
    if dummy_data:
        return {
            'labels': [f'User {i+1}' for i in range(10)],
            'data': [random.randint(5, 50) for _ in range(10)]
        }
    users = UserProfile.objects.annotate(robot_count=Count('user__owned_robots')) \
                .order_by('-robot_count')[:10]
    return {
        'labels': [user.user.username for user in users],
        'data': [user.robot_count for user in users]
    }

def get_robot_timeline(dummy_data=False):
    if dummy_data:
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        return {
            'labels': [d.strftime('%Y-%m-%d') for d in dates],
            'data': [random.randint(1, 20) for _ in dates]
        }
    robots = Robot.objects.extra({'created': "date(created_at)"}) \
              .values('created').annotate(count=Count('id'))
    return {
        'labels': [r['created'] for r in robots],
        'data': [r['count'] for r in robots]
    }

def get_alert_timeline(dummy_data=False):
    if dummy_data:
        dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
        return {
            'labels': [d.strftime('%Y-%m-%d') for d in dates],
            'data': [random.randint(1, 50) for _ in dates]
        }
    alerts = Alert.objects.extra({'created': "date(timestamp)"}) \
              .values('created').annotate(count=Count('alert_id'))
    return {
        'labels': [a['created'] for a in alerts],
        'data': [a['count'] for a in alerts]
    }
