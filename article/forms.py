# 引入表单类
from django import forms
# 引入文章模型
from .models import ArticlePost
# 引入CKEditorUploadingField
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils import timezone
from datetime import datetime, time


# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    # 使用CKEditor富文本编辑器
    body = forms.CharField(widget=CKEditorUploadingWidget())
    # 明确指定avatar为非必填字段
    avatar = forms.ImageField(required=False)
    # 添加created字段，用于设置发布时间
    created_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text='管理员可设置发布日期'
    )
    created_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text='管理员可设置发布时间'
    )
    
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'tags', 'avatar')
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ArticlePostForm, self).__init__(*args, **kwargs)
        # 如果是编辑现有文章，设置初始日期时间值
        if self.instance and self.instance.pk:
            self.fields['created_date'].initial = self.instance.created.date()
            self.fields['created_time'].initial = self.instance.created.time()
            
    def save(self, commit=True):
        article = super(ArticlePostForm, self).save(commit=False)
        
        # 如果用户是管理员且提供了日期和时间，则设置创建时间
        if self.user and self.user.is_superuser and self.cleaned_data.get('created_date') and self.cleaned_data.get('created_time'):
            # 合并日期和时间为datetime对象
            created_datetime = datetime.combine(
                self.cleaned_data['created_date'],
                self.cleaned_data['created_time']
            )
            # 转换为timezone aware
            article.created = timezone.make_aware(created_datetime)
            
            # 如果是新文章，同时设置更新时间与创建时间相同
            if not article.pk:
                article.updated = article.created
        
        if commit:
            article.save()
            self.save_m2m()
        
        return article