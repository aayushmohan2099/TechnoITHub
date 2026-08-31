from django.core.management.base import BaseCommand
from django.utils import timezone
from attendance.models import Attendance
from datetime import datetime, time

class Command(BaseCommand):
    help = 'Automatically punch out employees at midnight if they forgot to punch out.'

    def handle(self, *args, **kwargs):
        today = timezone.now().date()
        
        # 1. Woh saare records dhundho jinka punch_out abhi bhi None hai aur date aaj se pehle ki hai
        active_attendances = Attendance.objects.filter(punch_out__isnull=True, attendance_date__lt=today)

        count = 0
        for att in active_attendances:
            # 2. Uss din ki raat 11:59:59 PM par punch-out time set kar do
            end_of_day = timezone.make_aware(datetime.combine(att.attendance_date, time(23, 59, 59)))
            
            att.punch_out = end_of_day
            
            # Total seconds bhi calculate karke save kar do
            duration = att.punch_out - att.punch_in
            att.total_seconds = int(duration.total_seconds())
            
            att.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully auto-punched out {count} employees.'))