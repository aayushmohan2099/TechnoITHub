from django.core.management.base import BaseCommand
from accounts.models import CustomUser
from employees.models import EmployeeProfile
from tasks.models import Task
from attendance.models import Attendance
from django.utils import timezone
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generates 10 dummy employees with complete fields, tasks, and attendance'

    def handle(self, *args, **kwargs):
        self.stdout.write("🚀 Bulk dummy data generation started (Employees + Tasks + Attendance)...")

        employees_data = [
            {"name": "Aman Verma", "email": "aman.verma@ettm.com", "phone": "9876543201", "designation": "Backend Developer"},
            {"name": "Priya Sharma", "email": "priya.sharma@ettm.com", "phone": "9876543202", "designation": "Frontend Developer"},
            {"name": "Rahul Gupta", "email": "rahul.gupta@ettm.com", "phone": "9876543203", "designation": "UI/UX Designer"},
            {"name": "Neha Singh", "email": "neha.singh@ettm.com", "phone": "9876543204", "designation": "HR Manager"},
            {"name": "Amit Kumar", "email": "amit.kumar@ettm.com", "phone": "9876543205", "designation": "Project Manager"},
            {"name": "Sneha Patel", "email": "sneha.patel@ettm.com", "phone": "9876543206", "designation": "QA Engineer"},
            {"name": "Vikram Malhotra", "email": "vikram.m@ettm.com", "phone": "9876543207", "designation": "DevOps Engineer"},
            {"name": "Pooja Reddy", "email": "pooja.reddy@ettm.com", "phone": "9876543208", "designation": "Data Analyst"},
            {"name": "Rohit Mehra", "email": "rohit.mehra@ettm.com", "phone": "9876543209", "designation": "Full Stack Developer"},
            {"name": "Anjali Joshi", "email": "anjali.joshi@ettm.com", "phone": "9876543210", "designation": "Marketing Executive"},
        ]

        priorities = ['High', 'Medium', 'Low']
        statuses = ['Pending', 'In Progress', 'Completed']

        created_employees = 0
        created_tasks = 0
        created_attendance = 0

        for data in employees_data:
            email = data["email"]
            name = data["name"]
            password = "password123"

            # 1. Create or Get User & Employee Profile
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={'name': name}
            )
            
            if created:
                user.set_password(password)
                user.save()

                employee = EmployeeProfile.objects.create(
                    user=user,
                    employee_id=user.employee_id,
                    name=name,
                    email=email,
                    phone_number=data["phone"],
                    designation=data["designation"]
                )
                created_employees += 1
                self.stdout.write(self.style.SUCCESS(f"✔ Employee Created: [{employee.employee_id}] {name}"))
            else:
                employee = EmployeeProfile.objects.filter(user=user).first()
                self.stdout.write(self.style.WARNING(f"⚠ Employee already exists: {email}"))

            if user and employee:
                # 2. Add 2 Tasks for each employee
                for j in range(1, 3):
                    task_title = f"Task {j} for {name}"
                    if not Task.objects.filter(assigned_to=user, title=task_title).exists():
                        Task.objects.create(
                            assigned_to=user,
                            title=task_title,
                            description=f"Complete assigned modules for {data['designation']} role.",
                            priority=random.choice(priorities),
                            status=random.choice(statuses),
                            start_date=timezone.now().date(),
                            deadline=timezone.now().date() + timedelta(days=5)
                        )
                        created_tasks += 1

                # 3. Add Attendance Records for past 3 days (passing 'user' instead of 'employee')
                for days_ago in range(3):
                    att_date = timezone.now().date() - timedelta(days=days_ago)
                    
                    if not Attendance.objects.filter(employee=user, attendance_date=att_date).exists():
                        punch_in_time = timezone.now() - timedelta(days=days_ago, hours=8)
                        punch_out_time = punch_in_time + timedelta(hours=8)
                        total_secs = int((punch_out_time - punch_in_time).total_seconds())

                        Attendance.objects.create(
                            employee=user,
                            attendance_date=att_date,
                            punch_in=punch_in_time,
                            punch_out=punch_out_time,
                            total_seconds=total_secs
                        )
                        created_attendance += 1

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully Generated Summary:"))
        self.stdout.write(self.style.SUCCESS(f"- Total New Employees Added: {created_employees}"))
        self.stdout.write(self.style.SUCCESS(f"- Total Tasks Generated: {created_tasks}"))
        self.stdout.write(self.style.SUCCESS(f"- Total Attendance Records Generated: {created_attendance}"))