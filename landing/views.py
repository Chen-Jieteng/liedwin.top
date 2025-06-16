from django.shortcuts import render
from django.http import HttpResponse
import os

# Create your views here.

def download_app(request):
    """
    产品下载页面视图
    """
    # 读取并渲染React构建的HTML文件
    return render(request, 'landing/index.html')

def debug_static(request):
    """
    调试静态文件加载
    """
    return render(request, 'landing/debug.html')
