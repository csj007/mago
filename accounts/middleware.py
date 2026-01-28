# accounts/middleware.py
from django.utils import timezone
from .models import UserActivity
import re

# 排除静态文件和 admin 的频繁记录
EXCLUDE_URLS = [
    re.compile(r'\.(css|js|png|jpg|jpeg|gif|ico)$'),
    re.compile(r'^/admin/'),
    re.compile(r'^/favicon\.ico'),
]

class ActivityLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # 只记录已登录用户，并排除静态资源
        if request.user.is_authenticated:
            path = request.path
            if not any(pattern.match(path) for pattern in EXCLUDE_URLS):
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='view',
                    details=f"访问页面: {path}",
                    ip_address=self.get_client_ip(request)
                )

        return response

    def get_client_ip(self, request):
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded:
            return x_forwarded.split(',')[0]
        return request.META.get('REMOTE_ADDR')
