from django.shortcuts import render


def home(request):
    return render(request, 'pages/index.html', {
        'featured_post': None,
        'sidebar_posts': [],
        'latest_posts': [],
        'categories_with_posts': [],
    })


def faq(request):
    return render(request, 'pages/faq.html')


def privacy(request):
    return render(request, 'pages/privacy.html')


def terms(request):
    return render(request, 'pages/terms.html')


def newsletter_subscribe(request):
    # TODO: реализовать подписку
    from django.http import JsonResponse
    return JsonResponse({'status': 'ok'})