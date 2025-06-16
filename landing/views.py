from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings
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
    调试静态文件路径
    """
    debug_info = {
        'STATIC_URL': settings.STATIC_URL,
        'STATIC_ROOT': getattr(settings, 'STATIC_ROOT', 'Not set'),
        'STATICFILES_DIRS': getattr(settings, 'STATICFILES_DIRS', []),
        'BASE_DIR': getattr(settings, 'BASE_DIR', 'Not set'),
    }
    
    # 检查静态文件是否存在
    static_landing_path = os.path.join(settings.BASE_DIR, 'static', 'landing')
    if os.path.exists(static_landing_path):
        debug_info['landing_files'] = os.listdir(static_landing_path)
        
        # 检查具体文件
        css_file = os.path.join(static_landing_path, 'css', 'main.c2c6db73.css')
        js_file = os.path.join(static_landing_path, 'js', 'main.fdc8e9c5.js')
        manifest_file = os.path.join(static_landing_path, 'manifest.json')
        
        debug_info['file_exists'] = {
            'css': os.path.exists(css_file),
            'js': os.path.exists(js_file),
            'manifest': os.path.exists(manifest_file),
        }
    else:
        debug_info['landing_files'] = 'Directory does not exist'
        debug_info['file_exists'] = 'N/A'
    
    return JsonResponse(debug_info, indent=2)
