from accounts.models import User
from groups.models import Membership


def hs_space(request):
    return render(request, 'hs/hs_space.html')


def list_all_members(request):
    user_dict = {}

    for user in list(User.objects.all()):
        group_dict = {}

        for membership in list(Membership.objects.filter(person=user)):
            group_dict[membership.group.name] = membership.role

        user_dict[user] = group_dict

    return render(request, 'hs/all_members.html', {
        'userDict': user_dict,
        'users': User.objects.all(),
        'active': 'all_members',
        'total_members': len(User.objects.all()),
    })
