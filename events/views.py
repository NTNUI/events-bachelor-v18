from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def get_event_page(request):
    return render(request, 'events/events_main_page.html')
