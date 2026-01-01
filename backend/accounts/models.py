from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Менеджер для User без username"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя"""
    
    username = None  # Отключаем username
    email = models.EmailField('Email', unique=True)
    
    bio = models.TextField('О себе', blank=True)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    
    # Подписка
    is_premium = models.BooleanField('Премиум', default=False)
    subscription_end_date = models.DateTimeField('Окончание подписки', blank=True, null=True)
    stripe_customer_id = models.CharField('Stripe Customer ID', max_length=255, blank=True)
    
    # Paywall
    articles_read_count = models.PositiveIntegerField('Прочитано статей', default=0)
    articles_read_reset_date = models.DateField('Дата сброса счётчика', blank=True, null=True)
    
    # Уведомления
    newsletter_subscribed = models.BooleanField('Подписка на рассылку', default=True)
    comments_notify = models.BooleanField('Уведомления о комментариях', default=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.email
    
    @property
    def has_active_subscription(self):
        if self.is_premium and self.subscription_end_date:
            return self.subscription_end_date > timezone.now()
        return False


class Bookmark(models.Model):
    """Избранные статьи"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    post = models.ForeignKey('blog.Post', on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Закладка'
        verbose_name_plural = 'Закладки'
        unique_together = ['user', 'post']