# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from ..home import views

urlpatterns = [

    # The home page
    # path('', views.index, name='home'),
    path('', views.dashboard, name='dashboard'),
    # # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

    path('users/<int:user_id>/', views.get_user, name='user_details'),
    path('users/', views.users_dashboard, name='users_dashboard'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/bulk_delete/', views.bulk_delete_users, name='bulk_delete_users'),
    path('robots/', views.robot_dashboard, name='robot_dashboard'),
    path('robots/create/', views.create_robot, name='create_robot'),
    path('robots/bulk-delete/', views.bulk_delete_robots, name='bulk_delete_robots'),
    path('robots/<int:robot_id>/', views.robot_detail, name='robot_detail'),
]
