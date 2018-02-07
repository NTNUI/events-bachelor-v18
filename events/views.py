from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect as redirect

@login_required
def get_event_page(request):
    return render(request, 'events/events_main_page.html')

@login_required
def get_create_event_page(request):
    return render(request, 'events/create_new_event.html')

@login_required
def create_event(request):
    print('Hei!')
    if request.method == "POST":
        # add code to create database entry!
        print(str(request.POST.get('from_date')))
    return redirect('/events')