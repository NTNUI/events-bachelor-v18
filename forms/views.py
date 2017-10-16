from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from groups.models import SportsGroup
from .models import FormDoc


@login_required
def list_forms(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    forms = FormDoc.objects.all()
    return render(request, 'forms/forms_list.html', {
        'group': group,
        'forms' : forms,
        'slug': slug,
        'active': 'forms',
    })
