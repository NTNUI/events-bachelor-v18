from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from .models import SportsGroup, Membership
from .forms import NewInvitationForm


@login_required
def group_index(request, slug):
    return redirect('group_members', slug=slug)


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

    if request.method == 'POST':
        form = NewInvitationForm(request.POST, slug=slug)
        if form.is_valid():
            invitation = form.save()
            # TODO: change to redirect to 'group_invitations'
            return redirect('group_members', slug=slug)
    else:
        form = NewInvitationForm(slug=slug)

    # render group form
    return render(request, 'groups/invite_member.html', {
        'group': group,
        'slug': slug,
        'form': form,
    })


def list_groups(request):
    myGroups = []
    allGroups = []
    for membership in list(Membership.objects.filter(person=request.user)):
        myGroups.append(membership.group)

    allGroups = SportsGroup.objects.exclude(id__in=map(lambda x: x.id, myGroups))

    return render(request, 'groups/list_groups.html', {
        'myGroups': myGroups,
        'allGroups': allGroups,
    })
