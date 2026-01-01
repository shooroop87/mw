from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields
from taggit.managers import TaggableManager


class Category(TranslatableModel):
    """Категория статей"""
    
    translations = TranslatedFields(
        name=models.CharField('Название', max_length=100),
        description=models.TextField('Описание', blank=True),
    )
    slug = models.SlugField('Slug', unique=True)
    order = models.PositiveIntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order']
    
    def __str__(self):
        return self.safe_translation_getter('name', default=self.slug)
    
    def get_absolute_url(self):
        return reverse('blog:category', kwargs={'slug': self.slug})


class Post(TranslatableModel):
    """Статья блога"""
    
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Черновик'),
        (STATUS_PUBLISHED, 'Опубликовано'),
    ]
    
    translations = TranslatedFields(
        title=models.CharField('Заголовок', max_length=255),
        excerpt=models.TextField('Краткое описание', blank=True),
        content=models.TextField('Содержимое'),
    )
    
    slug = models.SlugField('Slug', unique=True, max_length=255)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name='Автор'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Категория'
    )
    
    image = models.ImageField('Изображение', upload_to='posts/', blank=True, null=True)
    
    status = models.CharField('Статус', max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    is_featured = models.BooleanField('Избранное', default=False)
    is_premium = models.BooleanField('Только для подписчиков', default=False)
    
    reading_time = models.PositiveIntegerField('Время чтения (мин)', default=5)
    views_count = models.PositiveIntegerField('Просмотры', default=0)
    
    tags = TaggableManager(blank=True)
    
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    published_at = models.DateTimeField('Опубликовано', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
        ordering = ['-published_at']
    
    def __str__(self):
        return self.safe_translation_getter('title', default=self.slug)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.safe_translation_getter('title', default='post'))
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Комментарий к статье"""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField('Текст')
    is_approved = models.BooleanField('Одобрен', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.author} - {self.post}'