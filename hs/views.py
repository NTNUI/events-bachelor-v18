from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import User

def list_all_members(request):
    return render(request, 'hs/hs_space.html')

