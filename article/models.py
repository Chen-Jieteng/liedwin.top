from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from taggit.managers import TaggableManager
from PIL import Image


class ArticleColumn(models.Model):

    title = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class ArticlePost(models.Model):
    
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='article/%Y%m%d/', blank=True)
    column = models.ForeignKey(
        ArticleColumn,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='article'
    )

    tags = TaggableManager(blank=True)

    title = models.CharField(max_length=100)

    body = models.TextField()

    total_views = models.PositiveIntegerField(default=0)

    likes = models.PositiveIntegerField(default=0)

    created = models.DateTimeField(default=timezone.now)

    updated = models.DateTimeField(auto_now=True)

    editor_type = models.CharField(max_length=1500, default='ckeditor')
    
    # 是否为草稿
    is_draft = models.BooleanField(default=False, verbose_name='是否草稿')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article:article_detail', args=[self.id])

    def save(self, *args, **kwargs):
        article = super(ArticlePost, self).save(*args, **kwargs)
        if self.avatar and not kwargs.get('update_fields'):
            if self.avatar.path.lower().endswith('.gif'):
                return
            img = Image.open(self.avatar)
            if img.format == 'GIF':
                frames = ImageSequence.Iterator(img)
    
                processed_frames = []
                for frame in frames:
                    frame = frame.convert('RGBA')
                    frame = frame.resize((400, int(frame.height * 400 / frame.width)), Image.LANCZOS)
                    processed_frames.append(frame)
    
                processed_frames[0].save(
                    self.avatar.path,
                    save_all=True,
                    append_images=processed_frames[1:],
                    loop=0,
                    duration=img.info['duration'],
                    disposal=img.info.get('disposal', 2)
                )
            else:
                img = Image.open(self.avatar)
                (x, y) = img.size
                new_x = 400
                new_y = int(new_x * (y / x))
                resized_image = img.resize((new_x, new_y), Image.LANCZOS)
                resized_image.save(self.avatar.path)


    def was_created_recently(self):
        diff = timezone.now() - self.created
        
        # if diff.days <= 0 and diff.seconds < 60:
        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            return True
        else:
            return False
