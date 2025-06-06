from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from comment.models import Comment
from comment.forms import CommentForm
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from taggit.models import Tag


# 文章列表
def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    draft = request.GET.get('draft')

    # 初始化查询集
    if draft == 'true' and request.user.is_authenticated:
        # 只有登录用户可以查看自己的草稿
        article_list = ArticlePost.objects.filter(author=request.user, is_draft=True)
    else:
        # 默认只显示非草稿文章
        article_list = ArticlePost.objects.filter(is_draft=False)

    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        # 将 search 参数重置为空
        search = ''

    # 栏目查询集
    column_name = ''
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)
        # 获取栏目名称，用于显示当前筛选条件
        try:
            column_obj = ArticleColumn.objects.get(id=column)
            column_name = column_obj.title
        except ArticleColumn.DoesNotExist:
            pass

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 查询集排序
    if order == 'total_views':
        # 按热度排序博文
        article_list = article_list.order_by('-total_views')
    elif order == 'comments':
        # 按评论数排序
        article_list = article_list.annotate(comment_count=Count('comments')).order_by('-comment_count')
    elif order == 'likes':
        # 按点赞数排序
        article_list = article_list.order_by('-likes')
    else:
        # 默认按照创建时间排序
        article_list = article_list.order_by('-created')

    # 获取所有栏目
    all_columns = ArticleColumn.objects.annotate(article_count=Count('article'))
    
    # 获取热门标签（最多使用的10个标签）
    hot_tags = Tag.objects.annotate(num_times=Count('taggit_taggeditem_items')).filter(num_times__gt=0).order_by('-num_times')[:10]

    # 每页显示 15 篇文章
    paginator = Paginator(article_list, 15)
    # 获取 url 中的页码
    page = request.GET.get('page')
    # 将导航对象相应的页码内容返回给 articles
    articles = paginator.get_page(page)
    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'column_name': column_name,
        'tag': tag,
        'all_columns': all_columns,
        'hot_tags': hot_tags,
        'draft': draft,
    }
    # render函数：载入模板，并返回context对象
    return render(request, 'article/list.html', context)


# 文章详情
def article_detail(request, id):
    # 取出相应的文章
    # article = ArticlePost.objects.get(id=id)
    # logger.warning('Something went wrong!')
    article = get_object_or_404(ArticlePost, id=id)
    
    # 取出文章评论
    comments = Comment.objects.filter(article=id)

    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 相邻发表文章的快捷导航
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id')
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id')
    if pre_article.count() > 0:
        pre_article = pre_article[0]
    else:
        pre_article = None

    if next_article.count() > 0:
        next_article = next_article[0]
    else:
        next_article = None

    # CKEditor内容不需要处理，目录将由JavaScript生成
    toc = ""

    # 为评论引入表单
    comment_form = CommentForm()

    # 需要传递给模板的对象
    context = { 
        'article': article,
        'toc': toc,
        'comments': comments,
        'pre_article': pre_article,
        'next_article': next_article,
        'comment_form': comment_form,
    }
    # 载入模板，并返回context对象
    return render(request, 'article/detail.html', context)


# 写文章的视图
@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(request.POST, request.FILES, user=request.user)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 指定栏目
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            # 指定作者
            new_article.author = request.user
            
            # 判断是否为草稿
            if 'save_draft' in request.POST:
                new_article.is_draft = True
            
            # 将新文章保存到数据库中
            new_article.save()
            # 保存 tags 的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm(user=request.user)
        # 获取所有栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文
        context = { 
            'article_post_form': article_post_form,
            'columns': columns 
        }
        # 返回模板
        return render(request, 'article/create.html', context)


# 删除文章，此方式有 csrf 攻击风险
@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")


# 安全删除文章
@login_required(login_url='/userprofile/login/')
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        if request.user != article.author:
            return HttpResponse("抱歉，你无权修改这篇文章。")
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")


# 更新文章
@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)

    # 过滤非作者的用户（管理员除外）
    if request.user != article.author and not request.user.is_superuser:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST, files=request.FILES, instance=article, user=request.user)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article = article_post_form.save(commit=False)
            # 更新栏目
            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
                
            # 判断是否为草稿
            if 'save_draft' in request.POST:
                article.is_draft = True
            else:
                article.is_draft = False
                
            article.save()
            # 保存标签的多对多关系
            article_post_form.save_m2m()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm(instance=article, user=request.user)
        # 获取所有栏目
        columns = ArticleColumn.objects.all()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 
            'article': article, 
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }
        # 将响应返回到模板中
        return render(request, 'article/update.html', context)


# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')


def article_list_example(request):
    """
    与下面的类视图做对比的函数
    简单的文章列表
    """
    if request.method == 'GET':
        articles_list = ArticlePost.objects.all()
        # 添加分页功能，每页15篇文章
        paginator = Paginator(articles_list, 15)
        # 获取 url 中的页码
        page = request.GET.get('page')
        # 将导航对象相应的页码内容返回给 articles
        articles = paginator.get_page(page)
        context = {'articles': articles}
        return render(request, 'article/list.html', context)



class ContextMixin:
    """
    Mixin
    """
    def get_context_data(self, **kwargs):
        # 获取原有的上下文
        context = super().get_context_data(**kwargs)
        # 增加新上下文
        context['order'] = 'total_views'
        return context


class ArticleListView(ContextMixin, ListView):
    """
    文章列表类视图
    """
    # 查询集的名称
    context_object_name = 'articles'
    # 模板
    template_name = 'article/list.html'
    # 分页，每页15篇文章
    paginate_by = 15

    def get_queryset(self):
        """
        查询集
        """
        queryset = ArticlePost.objects.filter(title='Python')
        return queryset


class ArticleDetailView(DetailView):
    """
    文章详情类视图
    """
    queryset = ArticlePost.objects.all()
    context_object_name = 'article'
    template_name = 'article/detail.html'

    def get_object(self):
        """
        获取需要展示的对象
        """
        # 首先调用父类的方法
        obj = super(ArticleDetailView, self).get_object()
        # 浏览量 +1
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        return obj


class ArticleCreateView(CreateView):
    """
    创建文章的类视图
    """
    model = ArticlePost
    fields = '__all__'
    # 或者有选择的提交字段，比如：
    # fields = ['title']
    template_name = 'article/create_by_class_view.html'
