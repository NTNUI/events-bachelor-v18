<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from groups.models import SportsGroup
=======
#from django.shortcuts import render
>>>>>>> 31e71f404e6dc8f9e8bffafed346d4eb310433cd

@login_required
def list(request, slug):
    group = get_object_or_404(SportsGroup, slug=slug)
    return render(request, 'forms/forms_list_base.html', {
        'group': group,
        'slug': slug,
        'active': 'forms',
    })
