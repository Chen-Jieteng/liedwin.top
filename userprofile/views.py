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
    显示用户的简历CV页面，带有树形结构展示
    如果id为None，则显示当前登录用户的CV
    如果未登录且id为None，则显示默认CV（站长的CV）
    """
    # 确定要显示的用户
    if id is not None:
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return HttpResponse("该用户不存在")
    elif request.user.is_authenticated:
        user = request.user
    else:
        # 未登录用户默认显示ID为1的用户CV（通常是站长）
        # 如果站长ID不是1，请替换为正确的ID
        try:
            user = User.objects.get(id=1)
        except User.DoesNotExist:
            # 如果ID为1的用户不存在，则尝试获取第一个用户
            try:
                user = User.objects.first()
                if not user:
                    return HttpResponse("系统中没有用户，无法显示CV")
            except:
                return HttpResponse("无法获取默认用户CV")
    
    # 获取用户资料
    if Profile.objects.filter(user=user).exists():
        profile = Profile.objects.get(user=user)
    else:
        profile = Profile.objects.create(user=user)
    
    # 准备简历数据（树结构）
    cv_data = {
        # 示例数据结构，实际应该从数据库或配置中获取
        'education': [
            {
                'degree': '硕士学位',
                'school': 'XX大学',
                'major': '计算机科学',
                'time': '2018-2021',
                'children': []
            },
            {
                'degree': '学士学位',
                'school': 'YY大学',
                'major': '软件工程',
                'time': '2014-2018',
                'children': []
            }
        ],
        'experience': [
            {
                'position': '高级开发工程师',
                'company': 'ABC科技有限公司',
                'time': '2021-至今',
                'description': '负责后端系统架构设计和开发',
                'children': [
                    {
                        'project': '企业管理系统',
                        'role': '技术负责人',
                        'time': '2022-2023',
                        'description': '设计并实现了基于Django的企业管理平台'
                    },
                    {
                        'project': '数据分析平台',
                        'role': '后端开发',
                        'time': '2021-2022',
                        'description': '负责数据处理管道和API设计'
                    }
                ]
            },
            {
                'position': '开发工程师',
                'company': 'XYZ公司',
                'time': '2018-2021',
                'description': '前端和后端开发',
                'children': []
            }
        ],
        'skills': [
            {
                'category': '编程语言',
                'items': ['Python', 'JavaScript', 'Java', 'C++'],
                'children': []
            },
            {
                'category': '框架',
                'items': ['Django', 'Flask', 'React', 'Vue.js'],
                'children': []
            },
            {
                'category': '其他',
                'items': ['数据库设计', 'RESTful API', '系统架构', 'DevOps'],
                'children': []
            }
        ]
    }
    
    context = {
        'user': user,
        'profile': profile,
        'cv_data': cv_data,
        'page_title': f"{user.username}的个人简历"
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
