import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alumed.settings")
django.setup()

from django_q.models import Schedule

# Check if the schedule already exists
if not Schedule.objects.filter(func='core.tasks.notify_upcoming_exams').exists():
    Schedule.objects.create(
        func='core.tasks.notify_upcoming_exams',
        schedule_type=Schedule.CRON,
        cron='0 9 * * *',
        repeats=-1  # Infinite
    )
    print("Registered notify_upcoming_exams cron job for 09:00 AM daily (via CRON).")
else:
    print("Cron job notify_upcoming_exams already registered.")
