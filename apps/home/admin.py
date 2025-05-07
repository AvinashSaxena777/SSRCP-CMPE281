# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserType, Organization, UserProfile, Robot, Alert, AIAnalytic, Schedule
# Register your models here.
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
    fields = ('userType', 'org', 'isActive')

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(UserType)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Organization)
admin.site.register(Robot)
admin.site.register(Alert)
admin.site.register(AIAnalytic)
admin.site.register(Schedule)