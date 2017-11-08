from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from hs.models import MainBoard
from django.contrib.auth.decorators import login_required
from hs.forms import SettingsForm
from django.contrib import messages
from groups.models import Membership


def get_base_hs_info():
    board = get_object_or_404(MainBoard, slug='hs')
    return {
        'board': board,
    }


@login_required
def hs_space(request):
    """Return the render for the main board view, hs"""
    base_info = get_base_hs_info()

    return render(request, 'hs/hs_base.html', {
        **base_info,
    })


@login_required
def list_all_members(request):
    """Return the render for /hs/allmembers"""
    base_info = get_base_hs_info()
    user_dict = {}  # a list of all the user's dictionaries

    for user in list(User.objects.all()):
        group_dict = {}  # one user's dictionary and his/her groups and respective roles

        for membership in list(Membership.objects.filter(person=user)):
            group_dict[membership.group.name] = membership.role

        user_dict[user] = group_dict

    return render(request, 'hs/all_members.html', {
        **base_info,
        'userDict': user_dict,
        'users': User.objects.all(),
        'active_tab': 'all_members',
        'total_members': len(User.objects.all()),
    })

@login_required
def hs_settings(request):
    slug = 'hs'
    base_info = get_base_hs_info()
    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, slug=slug)
        if form.is_valid():
            form.set_images()
            messages.success(request, 'Settings saved')
            return redirect('hs_settings')
    return render(request, 'hs/hs_settings.html', {
        'active_tab': 'hs_settings',
        **base_info,
    })
