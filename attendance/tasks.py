from celery import shared_task
from datetime import datetime, time
from django.utils import timezone
from attendance.models import Attendance


@shared_task
def auto_punch_out_task():
    today = timezone.now().date()
    active_attendances = Attendance.objects.filter(
        punch_out__isnull=True, attendance_date__lt=today
    )

    count = 0
    for att in active_attendances:
        end_of_day = timezone.make_aware(
            datetime.combine(att.attendance_date, time(23, 59, 59))
        )
        att.punch_out = end_of_day

        if att.punch_in:
            duration = att.punch_out - att.punch_in
            att.total_seconds = int(duration.total_seconds())

        att.save()
        count += 1

    return f'Successfully auto-punched out {count} employees.'