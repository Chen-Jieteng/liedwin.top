# 生产环境设置示例 - 请根据实际情况调整

# 安全设置
DEBUG = False
ALLOWED_HOSTS = ['www.liedwin.top', 'liedwin.top', 'your-server-ip']

# 静态文件设置
STATIC_URL = '/static/'
STATIC_ROOT = '/home/sites/liedwin.top/liedwin.top/staticfiles/'
STATICFILES_DIRS = [
    '/home/sites/liedwin.top/liedwin.top/static',
]

# 媒体文件设置
MEDIA_URL = '/media/'
MEDIA_ROOT = '/home/sites/liedwin.top/liedwin.top/media/'

# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 如果使用HTTPS
# SECURE_SSL_REDIRECT = True
# SECURE_HSTS_SECONDS = 31536000
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True 