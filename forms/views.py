from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required

@login_required
def list(request, slug):
    """return render(request, 'forms/forms_list.html', {
        #'group': group,
        'slug': slug,
        'active': 'forms_list',
    })"""
    return HttpResponse('Hello World')
