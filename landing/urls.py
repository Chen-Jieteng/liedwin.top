from django.urls import path
from . import views
from django.shortcuts import redirect

app_name = 'landing'

# 重定向函数，将带ID的CV路径重定向到标准CV页面
def cv_redirect(request, id):
    return redirect('userprofile:cv')

urlpatterns = [
    path('', views.download_app, name='download_app'),
    path('debug/', views.debug_static, name='debug_static'),
] 