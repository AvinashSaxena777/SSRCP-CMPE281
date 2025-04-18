# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from ..home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),

    # # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

    path('users/<int:user_id>/', views.get_user, name='user_details'),
    path('users/', views.users_dashboard, name='users_dashboard'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/update/', views.update_user, name='update_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/bulk_delete/', views.bulk_delete_users, name='bulk_delete_users'),
]
