from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from datetime import timedelta
from django.utils import timezone

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} - {self.email}" 
    
    
    

def email_verfication_expiry():
    return timezone.now() + timedelta(hours=24)

class EmailVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=email_verfication_expiry)  

    def __str__(self):
        return f"Verification for {self.user.email}"



def reset_password_expiry():
    return timezone.now() + timedelta(hours=1)

# class PasswordResetToken(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     token = models.UUIDField(default=uuid.uuid4)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField(default=reset_password_expiry)

#     def __str__(self):
#         return f"Reset token for {self.user.email}"

#     def is_expired(self):
#         return timezone.now() > self.expires_at


def otp_expiry():
    return timezone.now() + timedelta(minutes=15)


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=otp_expiry)
    is_used = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'password_reset_otp'
        verbose_name = 'Password Reset OTP'
        verbose_name_plural = 'Password Reset OTPs'

    def __str__(self):
        return f"OTP for {self.user.email}"

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def generate_otp():
        import random
        return str(random.randint(100000, 999999))
