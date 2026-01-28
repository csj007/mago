# accounts/signals.py
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import UserActivity
import re

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    # 获取 IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    # 获取 User-Agent
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    UserActivity.objects.create(
        user=user,
        activity_type='login',
        ip_address=ip,
        user_agent=user_agent,
        details=f"成功登录，IP: {ip}"
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    UserActivity.objects.create(
        user=user,
        activity_type='logout',
        ip_address=request.META.get('REMOTE_ADDR'),
        details="用户登出"
    )
