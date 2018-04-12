from django.shortcuts import render, redirect

from accounts.models import User
from .forms import SignUpForm
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from .api.updater import Updater


def signup(request):
    """signup is not in use"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user,
                       backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def add_all_users_from_exeline(request):
    if not request.user.is_superuser:
        return JsonResponse({
            'message': 'You can not do this.',
        })
    updater = Updater()
    added = updater.add_all_users_from_exeline()

    return JsonResponse({
        'message': 'Successfully added all members.',
        'members_updated_or_created': added,
    })


def add_last_week_users_from_exeline(request):
    if not request.user.is_superuser:
        return JsonResponse({
            'message': 'You can not do this.',
        })
    updater = Updater()
    added = updater.add_last_day_users_from_exeline()

    return JsonResponse({
        'message': 'Successfully added members from last day.',
        'members_updated_or_created': added,
    })


def get_user(request):
    user = request.user
    return JsonResponse({
        'first name': user.first_name,
        'last name': user.last_name,
        'email': user.email
    })
