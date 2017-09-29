from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def members(request):
    return render(request, 'groups/members.html')


def list_groups(request):
    return render(request, 'groups.html')
