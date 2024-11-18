# Generated by Django 5.1.3 on 2024-11-18 06:23

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('type', models.CharField(default='author', max_length=10)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('url', models.URLField(blank=True, editable=False, null=True, unique=True)),
                ('host', models.URLField()),
                ('display_name', models.CharField(max_length=100)),
                ('github', models.URLField(blank=True)),
                ('profile_image', models.URLField(blank=True)),
                ('page', models.URLField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Follows',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('remote_follower_url', models.URLField(blank=True, null=True)),
                ('is_remote', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('PENDING', 'Follow Request Pending'), ('ACCEPTED', 'Follow Request Accepted')], max_length=50)),
                ('followed_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='users.author')),
                ('local_follower_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.author')),
            ],
        ),
    ]
