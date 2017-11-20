from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.models import User
from groups.models import SportsGroup
from django.http import JsonResponse
from .forms import BoardChangeForm
from .models import BoardChange
from groups.views import get_base_group_info
from ntnui.decorators import is_member, is_board


@login_required
@is_member
def list_form(request, slug):
    base_info = get_base_group_info(request, slug)
    group = get_object_or_404(SportsGroup, slug=slug)

    if request.method == 'POST':
        if request.POST.get("openForm") == "Board Change Form":
            return redirect('forms_board_change', slug=slug)

    forms = []

    # Add 'board only' forms
    if request.user in group.active_board:
        bcf = {
            'name': 'Board Change Form',
            'description': 'Change the board members of your sports group with this form'
        }
        forms.append(bcf)  # Add the forms you want the view to see

    return render(request, 'forms/forms_list.html', {
        **base_info,
        'group': group,
        'forms': forms,
        'slug': slug,
        'active': 'forms',
    })


@login_required
@is_board
def board_change(request, slug):
    base_info = get_base_group_info(request, slug)
    group = get_object_or_404(SportsGroup, slug=slug)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BoardChangeForm(request.POST, slug=slug)

        # check whether it's valid:
        if form.is_valid():
            # If the form is valid perform the actions
            form.create_model()
            return redirect('forms_list', slug=slug)
        else:
            pass
    else:
        form = BoardChangeForm(slug=slug)

    return render(request, 'forms/forms_fill.html', {
        **base_info,
        'group': group,
        'slug': slug,
        'form': form,
        'active': 'forms',
    })


@login_required
def forms_list_submitted(request):
    user = request.user
    forms = []
    approved = []

    for f in BoardChange.objects.all():
        if user in f:
            if user in f.needs_approval_from():
                forms.append(f)
            elif f.needs_approval_from():
                approved.append(f)

    return render(request, 'forms/forms_list_submitted.html', {
        'approved': approved,
        'forms': forms
    })


@login_required
def forms_read(request, forms_id):
    try:
        form = BoardChange.objects.get(pk=forms_id)
        board = form.group.active_board
    except BoardChange.DoesNotExist:
        return redirect('404')

    if request.method == 'POST':
        if request.POST.get("button") == "approve":
            form.approve(request.user)

        return redirect('forms_list_submitted')

    return render(request, 'forms/forms_read.html', {
        'board': board,
        'form': form
    })

#
# AJAX Spesific Methods
#


@login_required
def ajax_validate_email(request):
    if request.method == "GET":
        email = request.GET.get('email', None)
        field_id = request.GET.get('id', None)

        try:
            user = User.objects.get(email=email)
            data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'id': field_id
            }
        except User.DoesNotExist:
            data = {
                'error': True,
                'id': field_id
            }

        return JsonResponse(data)


@login_required
def ajax_group_name(request):
    if request.method == "GET":
        slug = request.GET.get('group', None)

        try:
            group = SportsGroup.objects.get(slug=slug)
            data = {
                'group': group.name
            }
        except SportsGroup.DoesNotExist:
            data = {
                'error': True
            }

        return JsonResponse(data)
