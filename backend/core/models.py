from django.db import models


class NewsletterSubscriber(models.Model):
    """Подписчик рассылки"""
    
    email = models.EmailField('Email', unique=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Подписан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
    
    def __str__(self):
        return self.email