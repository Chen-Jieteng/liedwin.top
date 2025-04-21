from django.urls import path
from . import views

app_name = 'userprofile'

urlpatterns = [
    # 用户登录
    path('login/', views.user_login, name='login'),
    # 用户退出 - 更新URL模式添加时间戳支持
    path('logout/', views.user_logout, name='logout'),
    path('logout/<int:timestamp>/', views.user_logout, name='logout_with_timestamp'),
    # 用户注册
    path('register/', views.user_register, name='register'),
    # 用户删除
    path('delete/<int:id>/', views.user_delete, name='delete'),
    # 用户信息
    path('edit/<int:id>/', views.profile_edit, name='edit'),
    # 用户CV页面
    path('cv/', views.user_cv, name='cv'),
    path('cv/<int:id>/', views.user_cv, name='cv_with_id'),
    # 用户统计信息API
    path('api/stats/<int:id>/', views.user_stats_api, name='user_stats_api'),
]