from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SportsGroup, Membership, Invitation, Request
from .forms import NewInvitationForm, SettingsForm, JoinOpenGroupForm, JoinPrivateGroupForm, \
    LeaveGroupForm
from .helpers import get_group_role
from ntnui.decorators import is_member, is_board


def get_base_group_info(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    joined = request.user in group.members.all()
    try:
        Request.objects.get(person=request.user, group=group)
        sent_request = True
    except (Request.DoesNotExist, Request.MultipleObjectsReturned):
        sent_request = False
    return {
        'role': get_group_role(request.user, group),
        'group': group,
        'slug': slug,
        'active': 'about',
        'joined': joined,
        'sent_request': sent_request,
        'show_board': request.user.has_perm('groups.can_see_board', group),
        'show_members': request.user.has_perm('groups.can_see_members', group),
        'show_settings': request.user.has_perm('groups.can_see_settings', group),
        'show_group_settings': request.user.has_perm('groups.can_see_group_settings', group),
        'show_leave_button': request.user.has_perm('groups.can_leave_group', group),
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
    board_members = []
    board_core = []

    if request.method == 'POST':
        if group.public:
            form = JoinOpenGroupForm(slug=slug, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'You joined the group. Welcome!')
                return redirect('group_index', slug=slug)
        else:
            form = JoinPrivateGroupForm(slug=slug, user=request.user)
            if form.is_valid():
                form.save()
                return redirect('group_index', slug=slug)

    if request.user.has_perm('groups.can_see_board', group):
        group_members = Membership.objects.filter(group=group)
        board_members = set(group_members.exclude(role="member"))

        core = [
            ['President', group.active_board.president],
            ['Vice President', group.active_board.vice_president],
            ['Cashier', group.active_board.cashier]
        ]

        for person in core:
            membership = group.membership_set.get(person=person[1])
            if membership in board_members:
                board_members.remove(membership)

            board_core.append({'membership': membership, 'role': person[0]})
    return render(request, 'groups/group_info.html', {
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
def member_info(request, slug, member_id):
    group = get_object_or_404(SportsGroup, slug=slug)
    can_see_members = request.user.has_perm('groups.can_see_members', group)
    # TODO: sjekke om man faktisk har tilgang til å se medlemmer, basert på gruppe. Utrygt endepunkt
    try:
        member = Membership.objects.get(pk=member_id)
    except Membership.DoesNotExist:
        member = None
    return render(request, 'groups/ajax/member.html', {
        'role': get_group_role(request.user, group),
        'group': group,
        'slug': slug,
        'show_members': request.user.has_perm('groups.can_see_members', group),
        'member': member,
    })

@login_required
@is_board
def member_settings(request, slug, member_id):
    base_info = get_base_members_info(request, slug)
    try:
        member = Membership.objects.get(pk=member_id)
    except Membership.DoesNotExist:
        member = None
    return render(request, 'groups/member_settings.html', {
        **base_info,
        'member': member,
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
def downloads(request, slug):
    if request:
        pass
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")
    group = groups[0]


@login_required
def invite_member(request, slug):
    groups = SportsGroup.objects.filter(slug=slug)
    if len(groups) != 1:
        raise Http404("Group does not exist")

    if request.method == 'POST':
        form = NewInvitationForm(request.POST, slug=slug, user=request.user)
        if form.is_valid():
            invitation = form.save()
            messages.success(request, invitation.person.email+' invited')
            return redirect('group_invitations', slug=slug)
    else:
        form = NewInvitationForm(slug=slug)

    # Render group form
    return render(request, 'groups/invite_member.html', {
        **get_base_members_info(request, slug),
        'form': form,
    })


@login_required
def settings(request, slug):
    base_info = get_base_group_info(request, slug)

    if request.method == 'POST' and request.POST.get('save-settings'):
        form = SettingsForm(request.POST, request.FILES, slug=slug)
        print("IS VALID=!=!=!", form.is_valid())
        if form.is_valid():
            form.set_images()
            form.set_description()
            messages.success(request, 'Settings saved')
            return redirect('group_settings', slug=slug)

    if request.method == 'POST' and request.POST.get('leave-group'):
        form = LeaveGroupForm(slug=slug, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('group_index', slug=slug)

    return render(request, 'groups/group_settings.html', {
        **base_info,
        'active': 'settings',
        'member': request.user,
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
