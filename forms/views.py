from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from groups.models import SportsGroup


@login_required
def list_form(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    return render(request, 'forms/forms_list_base.html', {
        'group': group,
        'slug': slug,
        'active': 'forms',
    })

