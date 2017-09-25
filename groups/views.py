from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    return HttpResponse('Hello there, %s. This is the groups page.' % request.user.email)
