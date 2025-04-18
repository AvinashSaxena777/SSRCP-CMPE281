# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserType(models.Model):
    typeName = models.CharField(
        max_length=20,
        choices=[
            ('SUPER_ADMIN', 'Super Admin'),
            ('ADMIN', 'Admin'),
            ('STAFF', 'Staff'),
        ]
    )
    
    def __str__(self):
        return self.get_typeName_display()

class Organization(models.Model):
    organizationName = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    adminId = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='administered_organizations'
    )
    
    def __str__(self):
        return self.organizationName

class UserProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'  # Add this line
    )
    userType = models.ForeignKey(
        UserType, 
        on_delete=models.CASCADE,
        null=False,  # Keep this as required
        default=3  # Set default to Staff ID if exists
    )
    org = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    isActive = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile with default values
        UserProfile.objects.create(
            user=instance,
            userType=UserType.objects.get(typeName='STAFF'),  # Default type
            isActive=True
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    
class Robot(models.Model):
    id = models.AutoField(primary_key=True)
    modelName = models.CharField(max_length=255)
    simulationSession = models.IntegerField()
    robotId = models.IntegerField()
    cameraTop = models.CharField(max_length=255)
    cameraFront = models.CharField(max_length=255)
    version = models.FloatField()
    healthStatus = models.IntegerField()
    isActive = models.BooleanField(default=False)
    ownerId = models.ForeignKey(
        User,  # Use the custom user model
        on_delete=models.CASCADE, 
        related_name='owned_robots'
    )
    
    def __str__(self):
        return f"{self.modelName} - {self.robotId}"

class Alert(models.Model):
    alert_id = models.AutoField(primary_key=True)
    robot_id = models.ForeignKey(
        Robot, 
        on_delete=models.CASCADE, 
        related_name='alerts'
    )
    alert_type = models.IntegerField()
    description = models.IntegerField()
    severity = models.IntegerField()
    status = models.CharField(max_length=255)
    timestamp = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255)
    resolution_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Alert {self.alert_id} for Robot {self.robot_id.robotId}"


class AIAnalytic(models.Model):
    id = models.AutoField(primary_key=True)
    robot_id = models.ForeignKey(
        Robot, 
        on_delete=models.CASCADE, 
        related_name='ai_analyses'
    )
    frame = models.DateTimeField()
    detection_type = models.CharField(
        max_length=20, 
        choices=[
            ('fire', 'Fire'),
            ('violence', 'Violence'),
            ('accident', 'Accident'),
        ]
    )
    severity = models.CharField(
        max_length=10, 
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High'),
        ]
    )
    
    def __str__(self):
        return f"{self.detection_type} detected at {self.frame} - {self.severity} severity"
