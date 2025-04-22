from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.db.models import Count

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import UserLoginForm, UserRegisterForm

from .forms import ProfileForm
from .models import Profile

# 导入文章模型
from article.models import ArticlePost

# 个人CV视图
def user_cv(request, id=None):
    """
    显示个人简历CV页面
    """
    # 简化为直接渲染CV模板，不再进行用户判断和动态生成数据
    context = {
        'page_title': "陈杰腾的个人简历"
    }
    
    return render(request, 'userprofile/cv.html', context)

# 作者统计信息API
def user_stats_api(request, id):
    """
    API端点，返回作者的统计信息:
    - 文章数量
    - 粉丝数量
    - 关注数量
    """
    try:
        user = User.objects.get(id=id)
        
        # 获取用户的文章数
        article_count = ArticlePost.objects.filter(author=user).count()
        
        # TODO: 如果有粉丝和关注系统，在这里获取数据
        # 目前使用占位数据
        follower_count = 0
        following_count = 0
        
        data = {
            'article_count': article_count,
            'follower_count': follower_count,
            'following_count': following_count,
            'status': 'success'
        }
        
        return JsonResponse(data)
        
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': '用户不存在'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# Create your views here.

# 用户登录
def user_login(request):
    if request.method == 'POST':
        user_login_form = UserLoginForm(data=request.POST)
        if user_login_form.is_valid():
            # .cleaned_data 清洗出合法数据
            data = user_login_form.cleaned_data
            # 检验账号、密码是否正确匹配数据库中的某个用户
            # 如果均匹配则返回这个 user 对象
            user = authenticate(username=data['username'], password=data['password'])
            if user:
                # 将用户数据保存在 session 中，即实现了登录动作
                login(request, user)
                return redirect("article:article_list")
            else:
                return HttpResponse("账号或密码输入有误。请重新输入~")
        else:
            return HttpResponse("账号或密码输入不合法")
    elif request.method == 'GET':
        user_login_form = UserLoginForm()
        context = { 'form': user_login_form }
        return render(request, 'userprofile/login.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


# 用户退出
def user_logout(request):
    logout(request)
    return redirect("article:article_list")


# 用户注册
def user_register(request):
    if request.method == 'POST':
        user_register_form = UserRegisterForm(data=request.POST)
        if user_register_form.is_valid():
            new_user = user_register_form.save()
            # 保存好数据后立即登录并返回博客列表页面
            login(request, new_user)
            return redirect("article:article_list")
        else:
            # 使用默认的表单的check函数不仅会检查密码是否相同，还会检查密码复杂程度，以及是否与其他信息相关等等
            return HttpResponse("注册表单输入有误。请再次检查输入密码是否符合标准，并重新输入~")
    elif request.method == 'GET':
        user_register_form = UserRegisterForm()
        context = { 'form': user_register_form }
        return render(request, 'userprofile/register.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")


# 用户删除
# 验证用户是否登录的装饰器
@login_required(login_url='/userprofile/login/')
def user_delete(request, id):
    if request.method == 'POST':
        user = User.objects.get(id=id)
        # 验证登录用户、待删除用户是否相同
        if request.user == user:
            #退出登录，删除数据并返回博客列表
            logout(request)
            user.delete()
            return redirect("article:article_list")
        else:
            return HttpResponse("你没有删除操作的权限。")
    else:
        return HttpResponse("仅接受post请求。")


# 编辑用户信息
@login_required(login_url='/userprofile/login/')
def profile_edit(request, id):
    user = User.objects.get(id=id)

    # 旧教程代码
    # profile = Profile.objects.get(user_id=id)
    # 新教程代码： 获取 Profile
    if Profile.objects.filter(user_id=id).exists():
        # user_id 是 OneToOneField 自动生成的字段
        profile = Profile.objects.get(user_id=id)
    else:
        profile = Profile.objects.create(user=user)


    if request.method == 'POST':
        # 验证修改数据者，是否为用户本人
        if request.user != user:
            return HttpResponse("你没有权限修改此用户信息。")

        # 上传的文件保存在 request.FILES 中，通过参数传递给表单类
        profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            # 取得清洗后的合法数据
            profile_cd = profile_form.cleaned_data

            profile.phone = profile_cd['phone']
            profile.bio = profile_cd['bio']

            # 如果要求删除头像
            if 'remove_avatar' in request.POST and request.POST['remove_avatar'] == 'true':
                # 清除旧的头像文件
                if profile.avatar:
                    import os
                    if os.path.isfile(profile.avatar.path):
                        os.remove(profile.avatar.path)
                # 将头像字段置空
                profile.avatar = None
            # 如果有裁剪后的头像数据
            elif 'avatar_cropped' in request.POST and request.POST['avatar_cropped']:
                # 处理base64格式的图片数据
                import base64
                import os
                import uuid
                from django.core.files.base import ContentFile
                from datetime import datetime
                
                # 解析base64数据
                avatar_data = request.POST['avatar_cropped']
                # 去除MIME类型前缀 (例如 "data:image/jpeg;base64,")
                if ',' in avatar_data:
                    _, avatar_data = avatar_data.split(',', 1)
                    
                # 将base64数据转换为文件对象
                avatar_file = ContentFile(base64.b64decode(avatar_data))
                
                # 生成唯一文件名
                today = datetime.now().strftime('%Y%m%d')
                filename = f"avatar_{today}_{uuid.uuid4().hex}.jpg"
                file_path = os.path.join('avatar', today, filename)
                
                # 清除原有头像（如果存在）
                if profile.avatar:
                    try:
                        if os.path.isfile(profile.avatar.path):
                            os.remove(profile.avatar.path)
                    except Exception as e:
                        print(f"删除旧头像失败: {e}")
                
                # 保存新头像到模型
                profile.avatar.save(file_path, avatar_file, save=False)
            # 如果 request.FILES 存在文件，则保存（备用，一般不会执行到这里）
            elif 'avatar' in request.FILES:
                profile.avatar = profile_cd["avatar"]

            profile.save()
            # 带参数的 redirect()
            return redirect("userprofile:edit", id=id)
        else:
            return HttpResponse("注册表单输入有误。请重新输入~")

    elif request.method == 'GET':
        profile_form = ProfileForm()
        context = { 'profile_form': profile_form, 'profile': profile, 'user': user }
        return render(request, 'userprofile/edit.html', context)
    else:
        return HttpResponse("请使用GET或POST请求数据")
