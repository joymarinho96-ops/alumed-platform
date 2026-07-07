# Generated manually to fix missing table issue
#
# PodcastEpisode is already created in 0001_initial. This migration is
# kept as a no-op only to preserve the historical dependency chain.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_lesson_description'),
    ]

    operations = []
