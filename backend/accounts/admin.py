from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Bookmark


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_premium', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_premium', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личные данные', {'fields': ('first_name', 'last_name', 'bio', 'avatar')}),
        ('Подписка', {'fields': ('is_premium', 'subscription_end_date', 'stripe_customer_id')}),
        ('Paywall', {'fields': ('articles_read_count', 'articles_read_reset_date')}),
        ('Уведомления', {'fields': ('newsletter_subscribed', 'comments_notify')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password1', 'password2'),
        }),
    )


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('user', 'post')