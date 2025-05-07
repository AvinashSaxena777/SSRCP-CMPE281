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
    MODEL_CHOICES = [
        ('mercedes', 'Mercedes'),
        ('cheverolet', 'Cheverolet'),
        ('toyota', 'Toyota'),
        ('tesla', 'Tesla'),
    ]
    
    id = models.AutoField(primary_key=True)
    modelName = models.CharField(max_length=20, choices=MODEL_CHOICES)
    simulationSession = models.IntegerField()
    robotId = models.IntegerField(null=True, blank=True)
    cameraTop = models.CharField(max_length=255, null=True, blank=True)
    cameraFront = models.CharField(max_length=255, null=True, blank=True)
    version = models.FloatField(default=1.0)
    healthStatus = models.IntegerField(default=100)
    isActive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_robots'
    )

    def __str__(self):
        return f"{self.get_modelName_display()} - {self.robotId or 'New'}"

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
    alert_latitude = models.FloatField(default=None)
    alert_longitude = models.FloatField(default=None)
    status = models.CharField(max_length=255)
    timestamp = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255)
    resolution_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Alert {self.alert_id} for Robot {self.robot_id.robotId}"


class AIAnalytic(models.Model):
    DETECTION_TYPES = [
        ('fire', 'Fire'),
        ('violence', 'Violence'),
        ('accident', 'Accident'),
    ]
    SEVERITY_LEVELS = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    id = models.AutoField(primary_key=True)
    robot = models.ForeignKey(
        Robot, 
        on_delete=models.CASCADE,
        related_name='ai_analyses'
    )
    frame = models.DateTimeField()
    detection_type = models.CharField(
        max_length=20, 
        choices=DETECTION_TYPES
    )
    severity = models.CharField(
        max_length=10, 
        choices=SEVERITY_LEVELS
    )
    image = models.ImageField(
        upload_to='ai_analytics/',
        null=True,
        blank=True
    )
    is_valid = models.BooleanField(default=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return f"{self.get_detection_type_display()} detected at {self.frame}"
    
class Schedule(models.Model):
    STATUS_CHOICES = [
        ('Planned', 'Planned'),
        ('In Progress', 'In Progress'),
        ('Failed', 'Failed'),
        ('Completed', 'Completed'),
    ]
    
    id = models.AutoField(primary_key=True)
    robot = models.ForeignKey(
        Robot,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    start_latitude = models.FloatField()
    start_longitude = models.FloatField()
    dest_latitude = models.FloatField()
    dest_longitude = models.FloatField()
    scheduled_at = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Planned'
    )
    failure_error = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scheduled_tasks'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Schedule {self.id} - {self.robot} ({self.status})"
