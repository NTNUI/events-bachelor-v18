from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect as redirect, HttpResponse
from events.models import Event, EventDescription

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
        # Get prams from post
        from_date = request.POST.get('from_date')
        end_date = request.POST.get('end_date')
        host = request.POST.get('host')
        name = request.POST.get('name')
        description = request.POST.get('description')

        # Checks if priority is selected
        if request.POST.get('priority') is not None:
            priority = True
        else:
            priority = False

        # Checks if NTNUI is host
        if host == "NTNUI":
            is_ntnui = True
            host = None
        else:
            is_ntnui = False

        # Creates a new entry in the database
        try:
            event = Event.objects.create(start_date = from_date, end_date = end_date, priority = priority,
                             is_host_ntnui = is_ntnui)
            EventDescription.objects.create(name = name, description_text = description, language = "NO",
                                                               event = event)
        except Exception as e:
            print(e)
            # return failure
            return HttpResponse(status=400)

    # return success
    return HttpResponse(status=201)