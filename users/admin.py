from django.contrib import admin
from .models import User
from .models import EmailVerificationOTP
from .models import PasswordResetOTP
admin.site.site_header = "PixRevive Admin Portal"
admin.site.site_title = "My Project PixRevive Admin Portal"
admin.site.index_title = "Welcome to PixRevive Admin Portal"


admin.site.register(User)
admin.site.register(EmailVerificationOTP)
admin.site.register(PasswordResetOTP)