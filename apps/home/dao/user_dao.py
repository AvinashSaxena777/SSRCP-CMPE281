# home/dao/user_dao.py
from django.db import transaction
from django.contrib.auth.models import User
from .base_dao import BaseDAO
from ..models import UserProfile, Organization, UserType

class UserDAO(BaseDAO):
    model = User

    # dao/user_dao.py
    @classmethod
    @transaction.atomic
    def create_user(cls, user_data):
        try:
            user_type = UserType.objects.get(typeName=user_data['userType'])
            org = Organization.objects.get(id=int(user_data['org_id'])) if user_data.get('org_id') else None
            
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password']
            )
            
            user.profile.userType = user_type
            user.profile.org = org
            user.profile.save()
            
            if org and user_type.typeName == 'ADMIN':
                org.adminId = user
                org.save()
                
            return user
        except Exception as e:
            print(f"DAO Error: {str(e)}")
            raise


    @classmethod
    def get_all_active_users(cls):
        return cls.model.objects.filter(
            profile__isActive=True
        ).select_related('profile__userType', 'profile__org')

    @classmethod
    @transaction.atomic
    def update_user(cls, user_id, update_data):
        user = cls.get_by_id(user_id)
        profile = user.profile
        
        # Update core user fields
        if 'username' in update_data:
            user.username = update_data['username']
        if 'email' in update_data:
            user.email = update_data['email']
        if 'password' in update_data:
            user.set_password(update_data['password'])
        user.save()
        
        # Update profile fields
        if 'userType' in update_data:
            profile.userType = UserType.objects.get(id=update_data['userType'])
        if 'org_id' in update_data:
            new_org = Organization.objects.get(id=update_data['org_id'])
            
            if profile.org and profile.userType.typeName == 'ADMIN':
                profile.org.adminId = None
                profile.org.save()
            
            profile.org = new_org
            
            if profile.userType.typeName == 'ADMIN':
                new_org.adminId = user
                new_org.save()
        
        if 'isActive' in update_data:
            profile.isActive = update_data['isActive']
        
        profile.save()
        return user
    
    @classmethod
    def get_org_users(cls, organization):
        return cls.get_all_active_users().filter(profile__org=organization)

    @classmethod
    def get_all_org_users(cls):
        return cls.get_all_active_users()
