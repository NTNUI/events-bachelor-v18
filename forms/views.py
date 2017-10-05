from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required

@login_required
def list(request, slug):
    return HttpResponse('Hello World')
