from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from groups.models import SportsGroup
from .forms import BoardChangeForm


@login_required
def list_form(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    return render(request, 'forms/forms_list_base.html', {
        'group': group,
        'slug': slug,
        'active': 'forms',
    })


@login_required
def fill_form(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)

    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = BoardChangeForm(request.POST, slug=slug)

        # check whether it's valid:
        if form.is_valid():
            return redirect('forms_list', slug=slug)

    else:
        form = BoardChangeForm()

    return render(request, 'forms/forms_fill.html', {
        'group': group,
        'slug': slug,
        'form': form
    })
