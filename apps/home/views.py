# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .dao.user_dao import UserDAO
from .models import Organization
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from .models import UserType
from .dao.dashboard_dao import *
from .dao.robot_dao import RobotDAO
from django.db import transaction
import json


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))


@csrf_exempt
@require_http_methods(["POST"])
def create_user(request):
    try:
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'userType': request.POST.get('user_type'),  # Match form field name
            'org_id': request.POST.get('org_id')
        }
        
        user = UserDAO.create_user(data)
        messages.success(request, 'User created successfully')
        return redirect('users_dashboard')
    except Exception as e:
        messages.error(request, f'Error creating user: {str(e)}')
        return redirect('users_dashboard')

@require_http_methods(["GET"])
def get_all_active_users(request):
    try:
        users = UserDAO.get_all_active_users()
        result = [{
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'userType': u.profile.userType.typeName,
            'org_id': u.profile.org.id if u.profile.org else None,
            'org_name': u.profile.org.organizationName if u.profile.org else None,
            'isActive': u.profile.isActive,
            'last_updated': u.profile.last_updated
        } for u in users]
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def get_user(request, user_id):
    user = UserDAO.get_by_id(user_id)
    if not user:
        return JsonResponse({'error': 'User not found'}, status=404)
        
    profile = user.profile
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'userType': profile.userType.typeName,
        'org_id': profile.org.id if profile.org else None,
        'org_name': profile.org.organizationName if profile.org else None,
        'isActive': profile.isActive,
        'last_updated': profile.last_updated
    })

@csrf_exempt
@require_http_methods(["PUT"])
def update_user(request, user_id):
    try:
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'user_type': request.POST.get('user_type'),
            'org_id': request.POST.get('org_id'),
            'isActive': request.POST.get('isActive', 'off') == 'on'
        }
        
        UserDAO.update_user(user_id, data)
        messages.success(request, 'User updated successfully')
        return redirect('users_dashboard')
    except Exception as e:
        messages.error(request, f'Error updating user: {str(e)}')
        return redirect('users_dashboard')

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user(request, user_id):
    try:
        user = UserDAO.delete(user_id)
        if user:
            messages.success(request, 'User deactivated successfully')
        else:
            messages.warning(request, 'User not found')
        return redirect('users_dashboard')
    except Exception as e:
        messages.error(request, f'Error deleting user: {str(e)}')
        return redirect('users_dashboard')

@login_required
def dashboard(request):
    dummy = 'dummy' in request.GET
    
    context = {
        'metrics': {
            'organizations': get_organization_count(),
            'users': get_user_count(),
            'robots': get_robot_count(),
            'alerts': get_alert_count()
        },
        'charts': {
            'org_dist': get_organization_distribution(dummy),
            'robot_owners': get_robot_ownership_distribution(dummy),
            'robot_timeline': get_robot_timeline(dummy),
            'alert_timeline': get_alert_timeline(dummy)
        }
    }
    return render(request, 'home/dashboard.html', context)


@login_required
def users_dashboard(request):
    try:
        current_user = request.user
        profile = current_user.profile
        
        if profile.userType.typeName == 'SUPER_ADMIN':
            owned_orgs = Organization.objects.all()
            users = UserDAO.get_all_org_users()
        else:
            owned_orgs = Organization.objects.filter(adminId=current_user)
            users = UserDAO.get_org_users(profile.org)

        return render(request, 'home/users_dashboard.html', {
            'users': users,  # Changed back to users with optimized query
            'owned_organizations': owned_orgs,
            'user_types': UserType.objects.all()
        })
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        messages.error(request, f'Error loading dashboard: {str(e)}')
        return redirect('home')

@login_required
@require_http_methods(["POST"])
def bulk_delete_users(request):
    user_ids = request.POST.getlist('user_ids')
    try:
        UserDAO.bulk_delete_users(user_ids, request.user)
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required    
def robot_dashboard(request):
    robots = RobotDAO.get_all_robots(request.user)
    return render(request, 'home/robots_dashboard.html', {
        'robots': robots,
        'model_choices': Robot.MODEL_CHOICES
    })

@transaction.atomic
def create_robot(request):
    if request.method == 'POST':
        try:
            RobotDAO.create_robot(request.POST, request.user)
            messages.success(request, 'Robot created successfully!')
            return redirect('robot_dashboard')
        except Exception as e:
            messages.error(request, f'Error creating robot: {str(e)}')
    return redirect('robot_dashboard')

@transaction.atomic
def bulk_delete_robots(request):
    if request.method == 'POST':
        robot_ids = request.POST.getlist('robot_ids')
        try:
            RobotDAO.bulk_delete(robot_ids)
            messages.success(request, f'{len(robot_ids)} robots deleted')
        except Exception as e:
            messages.error(request, f'Delete failed: {str(e)}')
    return redirect('robot_dashboard')

def robot_detail(request, robot_id):
    robot = get_object_or_404(Robot, id=robot_id)
    context = {
        'robot': robot,
        'health_status_class': 'success' if robot.healthStatus > 75 
                             else 'warning' if robot.healthStatus > 50 
                             else 'danger'
    }
    return render(request, 'home/robot.html', context)