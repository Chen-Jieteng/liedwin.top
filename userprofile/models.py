from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os
# 引入内置信号
# from django.db.models.signals import post_save
# 引入信号接收器的装饰器
# from django.dispatch import receiver


# 用户扩展信息
class Profile(models.Model):
    # 与 User 模型构成一对一的关系
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 电话号码字段
    phone = models.CharField(max_length=20, blank=True)
    # 头像
    avatar = models.ImageField(upload_to='avatar/%Y%m%d/', blank=True)
    # 个人简介
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return 'user {}'.format(self.user.username)
    
    def save(self, *args, **kwargs):
        # 调用父类的save方法保存模型
        super().save(*args, **kwargs)
        
        # 如果上传了头像，则处理图片
        if self.avatar and self.avatar.name:
            img_path = self.avatar.path
            # 判断文件是否存在
            if os.path.exists(img_path):
                with Image.open(img_path) as img:
                    # 保存原始格式
                    img_format = img.format
                    # 将图片转换为RGB模式（移除透明通道）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # 获取图片宽高
                    width, height = img.size
                    
                    # 对于方形图片，直接调整大小
                    if width == height:
                        new_size = (300, 300)
                        img = img.resize(new_size, Image.LANCZOS)
                    else:
                        # 对于非方形图片，先进行中心裁剪再调整大小
                        # 确定裁剪区域（取中心正方形区域）
                        if width > height:
                            left = (width - height) / 2
                            top = 0
                            right = (width + height) / 2
                            bottom = height
                        else:
                            left = 0
                            top = (height - width) / 2
                            right = width
                            bottom = (height + width) / 2
                        
                        # 裁剪图片
                        img = img.crop((left, top, right, bottom))
                        # 调整大小为300x300像素
                        img = img.resize((300, 300), Image.LANCZOS)
                    
                    # 保存处理后的图片，保持原始格式
                    img.save(img_path, format=img_format, quality=95)


# 旧教程中采用了信号接收函数，在后台添加User时有时会产生bug
# 已采用其他方法实现其功能，废除了此信号接收函数
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, created, **kwargs):
#     if not created:
#         instance.profile.save(by_signal=True)