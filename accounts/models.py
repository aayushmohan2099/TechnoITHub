from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        
        # Django password hashing use karna hai; plaintext store nahi karna
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields['employee_id'] = employee_id

        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Employee', 'Employee'),
    )
    
    # Columns specifically requested in Section 6
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    must_change_password = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_id' # Login using Employee ID[cite: 2]
    REQUIRED_FIELDS = ['email', 'name']

    def save(self, *args, **kwargs):
        # Auto-generate unique Employee ID[cite: 2]
        if not self.employee_id:
            last_user = CustomUser.objects.all().order_by('id').last()
            if last_user and last_user.employee_id.startswith('EMP-'):
                last_id_num = int(last_user.employee_id.split('-')[1])
                self.employee_id = f"EMP-{last_id_num + 1}"
            else:
                self.employee_id = "EMP-1001"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.employee_id})"