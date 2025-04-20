from django.db.models import Count, Q
from ..models import AIAnalytic
from datetime import datetime, timedelta
import random
from django.db.models import Count, Q, Case, When, IntegerField, Sum

def get_daily_alerts(dummy=False):
    if dummy:
        dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        return {
            'labels': dates,
            'data': [random.randint(1, 20) for _ in range(7)]
        }
    
    results = AIAnalytic.objects.extra(
        {'date': "date(created_at)"}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    return {
        'labels': [item['date'] for item in results],
        'data': [item['count'] for item in results]
    }

def get_detection_type_distribution(dummy=False):
    if dummy:
        return {
            'labels': ['Fire', 'Violence', 'Accident'],
            'data': [random.randint(10, 50) for _ in range(3)]
        }
    
    results = AIAnalytic.objects.values('detection_type').annotate(
        count=Count('id')
    )
    
    return {
        'labels': [item['detection_type'] for item in results],
        'data': [item['count'] for item in results]
    }

# def get_alert_status_distribution(dummy=False):
#     if dummy:
#         return {
#             'labels': ['Resolved', 'Unresolved'],
#             'data': [65, 35]
#         }
    
#     results = AIAnalytic.objects.aggregate(
#         resolved=Count('id', filter=Q(resolved=True)),
#         unresolved=Count('id', filter=Q(resolved=False))
#     )
    
#     return {
#         'labels': ['Resolved', 'Unresolved'],
#         'data': [results['resolved'], results['unresolved']]
#     }

# def get_validation_distribution(dummy=False):
#     if dummy:
#         return {
#             'labels': ['Valid', 'False'],
#             'data': [80, 20]
#         }
    
#     results = AIAnalytic.objects.aggregate(
#         valid=Count('id', filter=Q(is_valid=True)),
#         false=Count('id', filter=Q(is_valid=False))
#     )
    
#     return {
#         'labels': ['Valid', 'False'],
#         'data': [results['valid'], results['false']]
#     }

def get_alert_status_distribution(dummy=False):
    return {
            'labels': ['Resolved', 'Unresolved'],
            'data': [65, 35]
        }

    
    # return {
    #     'labels': ['Resolved', 'Unresolved'],
    #     'data': [results['resolved'], results['unresolved']]
    # }

def get_validation_distribution(dummy=False):
    return {
            'labels': ['Valid', 'False'],
            'data': [80, 20]
    }
    
    # results = AIAnalytic.objects.aggregate(
    #     valid=Count(Case(When(is_valid=True, then=1), output_field=IntegerField())),
    #     false=Count(Case(When(is_valid=False, then=1), output_field=IntegerField()))
    # )
    
    # return {
    #     'labels': ['Valid', 'False'],
    #     'data': [results['valid'], results['false']]
    # }