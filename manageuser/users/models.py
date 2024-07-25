from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, mobile, email):
        if not username:
            raise ValueError('Users must have a username')
        if not mobile:
            raise ValueError('Users must have a mobile number')
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            username=username,
            mobile=mobile,
            email=self.normalize_email(email),
        )
        user.save(using=self._db)
        return user

    def create_superuser(self, username, mobile, email, password):
        user = self.create_user(
            username=username,
            mobile=mobile,
            email=email,
        )
        user.is_admin = True
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    username = models.CharField(max_length=30, unique=True)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(max_length=255)
    fullname = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['mobile', 'email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin
