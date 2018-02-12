from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event, EventDescription
from django.utils.translation import gettext as _

"""Returnees the main page for events
"""


@login_required
def get_event_page(request):
    return render(request, 'events/events_main_page.html')


"""Returnees he page where events are created
"""


@login_required
def get_create_event_page(request):
    return render(request, 'events/create_new_event.html')


"""Creates a new event with the given data
"""


@login_required
def create_event(request):
    if request.method == "POST":
        # Get prams from post
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        host = request.POST.get('host')
        name = request.POST.get('name')
        description_text = request.POST.get('description_text')

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
            event = Event.objects.create(start_date = start_date, end_date = end_date, priority = priority,
                                         is_host_ntnui = is_ntnui)
            EventDescription.objects.create(name = name, description_text = description_text , language = "NO",
                                            event = event)
        except Exception as e:
            print(e)
            # return failure
            return JsonResponse({
                'message': _('Faild to create event!')},
                status = 400)

    # return success
    return JsonResponse({
        'message': _('New event successfully created!')},
         status=201)
