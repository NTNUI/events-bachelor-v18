from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User
from groups.models import Membership
from accounts.models import User


def hs_space(request):
    return render(request, 'hs/hs_space.html')


def list_all_members(request):
    group_dict = {}
    count = 0

    for user in list(User.objects.all()):
        temp = []

        for membership in list(Membership.objects.filter(person=user)):
            count += 1
            temp.append(membership.group.name)

        group_dict[user] = temp

    print(group_dict)

    return render(request, 'hs/all_members.html', {
        'groupDict': group_dict,
        'users': User.objects.all(),
        'active': 'all_members',
    })
