# 引入表单类
from django import forms
# 引入文章模型
from .models import ArticlePost
# 引入CKEditorUploadingField
from ckeditor_uploader.fields import RichTextUploadingField
from ckeditor_uploader.widgets import CKEditorUploadingWidget


# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    # 使用CKEditor富文本编辑器
    body = forms.CharField(widget=CKEditorUploadingWidget())
    
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'tags', 'avatar')