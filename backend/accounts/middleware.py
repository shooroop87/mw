from django.shortcuts import redirect
from django.urls import reverse


class OnboardingMiddleware:
    """Middleware для онбординга новых пользователей"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Пока просто пропускаем
        response = self.get_response(request)
        return response