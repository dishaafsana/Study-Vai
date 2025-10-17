from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, user_type=None):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, user_type=user_type)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(email, username, password, "Admin")
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    joined_group = models.ForeignKey(
        "Groups.Group", blank=True, null=True, on_delete=models.SET_NULL, related_name="members"
    )
    USER_TYPE_CHOICES = (
        ("student", "Student"),
        ("TeamLeader", "TeamLeader"),
    )
    profile_picture = models.ImageField(upload_to="profile_pics/", blank=True, null=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150)
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    class_name = models.CharField(max_length=100, blank=True, null=True)
    school_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    qualification = models.CharField(max_length=255, blank=True, null=True)
    subjects_taught = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username
