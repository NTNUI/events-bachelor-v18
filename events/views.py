from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from events.models import Event, EventDescription
from django.utils.translation import gettext as _

"""Returns the main page for events
"""
@login_required
def get_event_page(request):
    return render(request, 'events/events_main_page.html')


"""Returns the page where events are created
"""
@login_required
def get_create_event_page(request):
    return render(request, 'events/create_new_event.html')


"""Creates a new event with the given data
"""
@login_required
def create_event(request):
    if request.method == "POST":
        entry_created = create_database_entry_for_event_from_post(request)
        if entry_created:
            return JsonResponse({'message': 'New event successfully created!'},
                                status=201)
    return JsonResponse({
        'message': 'Failed to create event!'},
        status=400)


""" Creates database entry from POST message.
"""
def create_database_entry_for_event_from_post(request):
    description_text, end_date, host, name, start_date = get_params_from_post(request)
    priority = priority_is_selected(request)
    is_ntnui = ntnui_is_host(host)
    return create_and_validate_database_entry(description_text, end_date, is_ntnui, name, priority, start_date)

""" Returns parameters from POST message.
"""
def get_params_from_post(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    host = request.POST.get('host')
    name = request.POST.get('name')
    description_text = request.POST.get('description_text')
    return description_text, end_date, host, name, start_date


""" Checks whether the event is priorized or not.
"""
def priority_is_selected(request):
    if request.POST.get('priority') is not None:
        priority = True
    else:
        priority = False
    return priority


""" Checks whether NTNUI is hosting the event or not.
"""
def ntnui_is_host(host):
    if host == "NTNUI":
        is_ntnui = True
        host = None
    else:
        is_ntnui = False
    return is_ntnui


""" Tries to create an entry in the database for the event described in the POST message.
The entry is validated, as well.
"""
def create_and_validate_database_entry(description_text, end_date, is_ntnui, name, priority, start_date):
    try:
        event = Event.objects.create(start_date=start_date, end_date=end_date, priority=priority,
                                     is_host_ntnui=is_ntnui)
        EventDescription.objects.create(name=name, description_text=description_text, language="NO",
                                        event=event)
    except Exception as e:
        print(e)
        return False
    return True

