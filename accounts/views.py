from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login as auth_login

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', { 'form': form })
