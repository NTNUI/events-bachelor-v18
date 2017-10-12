from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import SportsGroup, Membership, Invitation
from .forms import NewInvitationForm, SettingsForm


@login_required
def group_index(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    return render(request, 'groups/info.html', {
        'group': group,
        'slug': slug,
        'active': 'about'
    })


@login_required
def members(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    invitations = Invitation.objects.filter(group=group.pk)
    members = Membership.objects.filter(group=group.pk)
    return render(request, 'groups/members.html', {
        'group': group,
        'members': members,
        'total_members': len(members),
        'total_invitations': len(invitations),
        'slug': slug,
        'active_tab': 'members',
        'active': 'members'
    })


@login_required
def invitations(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    invitations = Invitation.objects.filter(group=group.pk)
    members = Membership.objects.filter(group=group.pk)
    return render(request, 'groups/invitations.html', {
        'group': group,
        'invitations': invitations,
        'total_invitations': len(invitations),
        'total_members': len(members),
        'slug': slug,
        'active_tab': 'invitations',
        'active': 'members',
    })


@login_required
def invite_member(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")
    group = groups[0]

    if request.method == 'POST':
        form = NewInvitationForm(request.POST, slug=slug)
        if form.is_valid():
            invitation = form.save()
            # TODO: change to redirect to 'group_invitations'
            return redirect('group_invitations', slug=slug)
    else:
        form = NewInvitationForm(slug=slug)

    # render group form
    return render(request, 'groups/invite_member.html', {
        'group': group,
        'slug': slug,
        'form': form,
        'active': 'members',
    })


@login_required
def settings(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")
    group = groups[0]

    if request.method == 'POST':
        form = SettingsForm(request.POST, slug=slug)

        if form.is_valid():
            return redirect('group_settings', slug=slug)

    return render(request, 'groups/settings.html', {
        'group': group,
        'slug': slug,
        'active': 'settings',
    })


@login_required
def list_groups(request):
    myGroups = []
    allGroups = []
    for membership in list(Membership.objects.filter(person=request.user)):
        myGroups.append(membership.group)

    allGroups = SportsGroup.objects.exclude(
        id__in=map(lambda x: x.id, myGroups))

    return render(request, 'groups/list_groups.html', {
        'myGroups': myGroups,
        'allGroups': allGroups,
    })
