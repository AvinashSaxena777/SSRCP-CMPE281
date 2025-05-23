# Generated by Django 3.2.6 on 2025-04-18 20:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizationName', models.CharField(max_length=255)),
                ('isActive', models.BooleanField(default=True)),
                ('adminId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='administered_organizations', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('typeName', models.CharField(choices=[('SUPER_ADMIN', 'Super Admin'), ('ADMIN', 'Admin'), ('STAFF', 'Staff')], max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isActive', models.BooleanField(default=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('org', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='home.organization')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
                ('userType', models.ForeignKey(default=3, on_delete=django.db.models.deletion.CASCADE, to='home.usertype')),
            ],
        ),
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('modelName', models.CharField(max_length=255)),
                ('simulationSession', models.IntegerField()),
                ('robotId', models.IntegerField()),
                ('cameraTop', models.CharField(max_length=255)),
                ('cameraFront', models.CharField(max_length=255)),
                ('version', models.FloatField()),
                ('healthStatus', models.IntegerField()),
                ('isActive', models.BooleanField(default=False)),
                ('ownerId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_robots', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('alert_id', models.AutoField(primary_key=True, serialize=False)),
                ('alert_type', models.IntegerField()),
                ('description', models.IntegerField()),
                ('severity', models.IntegerField()),
                ('status', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('resolved_by', models.CharField(max_length=255)),
                ('resolution_time', models.DateTimeField(blank=True, null=True)),
                ('robot_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='home.robot')),
            ],
        ),
        migrations.CreateModel(
            name='AIAnalytic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('frame', models.DateTimeField()),
                ('detection_type', models.CharField(choices=[('fire', 'Fire'), ('violence', 'Violence'), ('accident', 'Accident')], max_length=20)),
                ('severity', models.CharField(choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')], max_length=10)),
                ('robot_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_analyses', to='home.robot')),
            ],
        ),
    ]
