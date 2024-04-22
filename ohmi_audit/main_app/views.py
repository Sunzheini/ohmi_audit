from django.shortcuts import render


def index_view(request):
    return render(request, 'index.html')


def about_view(request):
    return render(request, 'index.html')


def contact_view(request):
    return render(request, 'index.html')


def login_view(request):
    return render(request, 'index.html')


def register_view(request):
    return render(request, 'index.html')


def logout_view(request):
    return render(request, 'index.html')
