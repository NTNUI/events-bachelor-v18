from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import SportsGroup, Membership


@login_required
def members(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if (len(groups) != 1):
        raise Http404("Group does not exist")
    group = groups[0]
    members = Membership.objects.filter(group=group.pk)
    return render(request, 'groups/members.html', {
        'group': group,
        'members': members,
        'total_members': len(members),
        'slug': slug,
    })


@login_required
def invite_member(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if (len(groups) != 1):
        raise Http404("Group does not exist")
    group = groups[0]

    # render group form
    return render(request, 'groups/invite_member.html', {
        'group': group,
        'slug': slug,
    })


def list_groups(request):
    return render(request, 'groups/list_groups.html')
