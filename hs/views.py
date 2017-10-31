from django.shortcuts import render
from accounts.models import User
from groups.models import Membership
from django.contrib.auth.decorators import login_required


@login_required
def hs_space(request):
    """Return the render for the main board view, /hs"""
    return render(request, 'hs/hs_space.html')


@login_required
def list_all_members(request):
    """Return the render for /hs/allmembers"""
    user_dict = {}  # a list of all the user's dictionaries

    for user in list(User.objects.all()):
        group_dict = {}  # one user's dictionary and his/her groups and respective roles

        for membership in list(Membership.objects.filter(person=user)):
            group_dict[membership.group.name] = membership.role

        user_dict[user] = group_dict

    return render(request, 'hs/all_members.html', {
        'userDict': user_dict,
        'users': User.objects.all(),
        'active_tab': 'all_members',
        'total_members': len(User.objects.all()),
    })
