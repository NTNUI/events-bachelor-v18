from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from rules.contrib.views import permission_required
from .models import SportsGroup, Membership, Invitation
from .forms import NewInvitationForm, SettingsForm
from .helpers import get_group_role


def get_group_by_slug(request, slug):
    return get_object_or_404(SportsGroup, slug=slug)


def get_base_group_info(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    return {
        'role': get_group_role(request.user, group),
        'group': group,
        'slug': slug,
        'show_board': request.user.has_perm('groups.can_see_board', group),
        'show_members': request.user.has_perm('groups.can_see_members', group),
        'show_settings': request.user.has_perm('groups.can_see_settings', group),
        'show_forms': request.user.has_perm('groups.can_see_forms', group),
    }


def get_base_members_info(request, slug):
    base_info = get_base_group_info(request, slug)
    invitations = Invitation.objects.filter(group=base_info['group'].pk)
    members = Membership.objects.filter(group=base_info['group'].pk)
    return {
        **base_info,
        'invitations': invitations,
        'total_invitations': len(invitations),
        'members': members,
        'total_members': len(members),
        'active': 'members',
    }


@login_required
def group_index(request, slug):
    return render(request, 'groups/info.html', {
        **get_base_group_info(request, slug),
        'active': 'about'
    })


@login_required
@permission_required('groups.can_see_members', fn=get_group_by_slug)
def members(request, slug):
    return render(request, 'groups/members.html', {
        **get_base_members_info(request, slug),
        'active_tab': 'members',
    })


@login_required
def invitations(request, slug):
    return render(request, 'groups/invitations.html', {
        **get_base_members_info(request, slug),
        'active_tab': 'invitations',
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
    base_info = get_base_group_info(request, slug)

    if request.method == 'POST':
        form = SettingsForm(request.POST, slug=slug)
        if form.is_valid():
            return redirect('group_settings', slug=slug)

    return render(request, 'groups/settings.html', {
        **base_info,
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
