from django.contrib import admin
# 记得引入include
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

import notifications.urls

from article.views import article_list


# 存放了映射关系的列表
urlpatterns = [
    path('admin/', admin.site.urls),
    # home
    path('', article_list, name='home'),
    # 重置密码app
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('password-reset-recover/', auth_views.PasswordResetView.as_view(), name='password_reset_recover'),

    # 新增代码，配置app的url
    path('article/', include('article.urls', namespace='article')),
    # 用户管理
    path('userprofile/', include('userprofile.urls', namespace='userprofile')),
    # 评论
    path('comment/', include('comment.urls', namespace='comment')),
    # djang-notifications
    path('inbox/notifications/', include(notifications.urls, namespace='notifications')),
    # notice
    path('notice/', include('notice.urls', namespace='notice')),
    # django-allauth
    path('accounts/', include('allauth.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
