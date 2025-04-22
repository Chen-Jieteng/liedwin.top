from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'userprofile'

# 重定向函数，将带ID的CV路径重定向到标准CV页面
def cv_redirect(request, id):
    return redirect('userprofile:cv')

urlpatterns = [
    # 用户登录
    path('login/', views.user_login, name='login'),
    # 用户退出
    path('logout/', views.user_logout, name='logout'),
    # 用户注册
    path('register/', views.user_register, name='register'),
    # 用户删除
    path('delete/<int:id>/', views.user_delete, name='delete'),
    # 用户信息
    path('edit/<int:id>/', views.profile_edit, name='edit'),
    # 个人简历页面 - 简化为单一路径
    path('cv/', views.user_cv, name='cv'),
    # 旧格式CV路径的重定向
    path('cv/<int:id>/', cv_redirect, name='cv_with_id'),
    # 用户统计信息API
    path('api/stats/<int:id>/', views.user_stats_api, name='user_stats_api'),
]