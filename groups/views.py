from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .models import SportsGroup, Membership, Invitation, Request
from .forms import NewInvitationForm, SettingsForm, JoinOpenGroupForm, JoinPrivateGroupForm
from .helpers import get_group_role


def get_base_group_info(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    joined = request.user in group.members.all()
    return {
        'role': get_group_role(request.user, group),
        'group': group,
        'slug': slug,
        'active': 'about',
        'joined': joined,
        'show_board': request.user.has_perm('groups.can_see_board', group),
        'show_members': request.user.has_perm('groups.can_see_members', group),
        'show_settings': request.user.has_perm('groups.can_see_settings', group),
        'show_forms': request.user.has_perm('groups.can_see_forms', group),
    }


def get_base_members_info(request, slug):
    base_info = get_base_group_info(request, slug)
    invitations = Invitation.objects.filter(group=base_info['group'].pk)
    members = Membership.objects.filter(group=base_info['group'].pk)
    requests = Request.objects.filter(group=base_info['group'].pk)
    return {
        **base_info,
        'invitations': invitations,
        'total_invitations': len(invitations),
        'requests': requests,
        'total_requests': len(requests),
        'members': members,
        'total_members': len(members),
        'active': 'members',
        'show_new_invitation': request.user.has_perm(
            'groups.can_invite_member', base_info['group']),
    }


@login_required
def group_index(request, slug):
    base_info = get_base_group_info(request, slug)
    group = base_info['group']

    if request.method == 'POST':
        if group.public:
            form = JoinOpenGroupForm(slug=slug, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('group_index', slug=slug)
        else:
            form = JoinPrivateGroupForm(slug=slug, user=request.user)
            if form.is_valid():
                form.save()

    board_members = []
    board_core = []
    if request.user.has_perm('groups.can_see_board', group):
        board_members = set(group.membership_set.filter(in_board=True))
        core = [
            ['President', group.board.president],
            ['Vice President', group.board.vice_president],
            ['Cashier', group.board.cashier]
        ]
        for person in core:
            membership = group.membership_set.get(person=person[1])
            board_members.remove(membership)
            board_core.append({'membership': membership, 'role': person[0]})
    return render(request, 'groups/info.html', {
        **base_info,
        'active': 'about',
        'board_core': board_core,
        'board_members': board_members,
    })


@login_required
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
def requests(request, slug):
    if request.method == 'POST':
        requestID = request.POST.get("request_id", "")
        result = request.POST.get("result", "")
        if result == "Yes":
            joinRequest = Request.objects.get(pk=requestID)
            Membership.objects.create(person=joinRequest.person, group=joinRequest.group)
            joinRequest.delete()
        elif result == "No":
            joinRequest = Request.objects.get(pk=requestID)
            joinRequest.delete()
        else:
            raise Http404("Request does not exist")

    return render(request, 'groups/requests.html', {
        **get_base_members_info(request, slug),
        'active_tab': 'requests',
    })

@login_required
def download_members(request, slug): # TODO: add permissions
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")
    group = groups[0]

    return render(request, 'groups/download_members.html', {
        **get_base_members_info(request, slug),
        'active': 'members',
    })



@login_required
def invite_member(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")
    group = groups[0]

    if request.method == 'POST':
        form = NewInvitationForm(request.POST, slug=slug, user=request.user)
        if form.is_valid():
            invitation = form.save()
            # TODO: change to redirect to 'group_invitations'
            return redirect('group_invitations', slug=slug)
    else:
        form = NewInvitationForm(slug=slug)

    # render group form
    return render(request, 'groups/invite_member.html', {
        **get_base_members_info(request, slug),
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
    my_groups = []
    for membership in list(Membership.objects.filter(person=request.user)):
        my_groups.append(membership.group)

    all_groups = SportsGroup.objects.exclude(
        id__in=map(lambda x: x.id, my_groups))

    return render(request, 'groups/list_groups.html', {
        'my_groups': my_groups,
        'all_groups': all_groups,
    })
