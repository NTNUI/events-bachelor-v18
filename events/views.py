from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Event, EventDescription
from hs.models import MainBoardMembership
from groups.models import Board, SportsGroup
from django.utils.translation import gettext as _

"""Returns the main page for events
"""
@login_required
def get_event_page(request):
    #Used to find out if the create-event button shall be rendered or not
    can_create_event = user_can_create_event(request.user)
    return render(request, 'events/events_main_page.html',{
                'can_create_event': can_create_event
                  })


"""Checks to see if a user can create event of any kind"""
def user_can_create_event(user):
    # User is in MainBoard
    if MainBoardMembership.objects.filter(person_id=user).exists():
        return True
    # Checks if the user is in any active board
    for board in Board.objects.filter(president=user) | \
            Board.objects.filter(vice_president=user) | \
            Board.objects.filter(cashier=user):
        # Checks that the board is active
        if SportsGroup.objects.filter(active_board=board):
            return True
    return False


"""Returns the page where events are created"""
@login_required
def get_create_event_page(request):
    groups = user_can_create_events_for_groups(request.user)
    return render(request, 'events/create_new_event.html',
                  {'groups': groups})


"""Finds the groups a user can create events for"""
def user_can_create_events_for_groups(user):
    # Create an empty return list
    return_list = []

    # Adds NTNUI if member of hs
    if MainBoardMembership.objects.filter(person_id=user).exists():
        return_list.append({'id': "", 'name': 'NTNUI'})

    # Finds all the groups were the user is in the board
    for board in Board.objects.filter(president=user) | \
            Board.objects.filter(vice_president=user) | \
            Board.objects.filter(cashier=user):

        #Checks that the board is active
        for group in SportsGroup.objects.filter(active_board = board):
            return_list.append(group)

    return return_list



"""Creates a new event with the given data"""
@login_required
def create_event(request):
    print(request)
    if request.method == "POST":
        entry_created = create_database_entry_for_event_from_post(request)
        if entry_created:
            return JsonResponse({'message': _('New event successfully created!')},
                                status=201)
    return JsonResponse({
        'message': _('Failed to create event!')},
        status=400)


""" Creates database entry from POST message."""
def create_database_entry_for_event_from_post(request):
    description_text, end_date, host, name, start_date = get_params_from_post(request)
    priority = priority_is_selected(request)
    is_ntnui = ntnui_is_host(host)
    return create_and_validate_database_entry(description_text, end_date, is_ntnui, name, priority, start_date)

""" Returns parameters from POST message."""
def get_params_from_post(request):
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    host = request.POST.get('host')
    name = request.POST.get('name')
    description_text = request.POST.get('description_text')
    return description_text, end_date, host, name, start_date


""" Checks whether the event is priorized or not."""
def priority_is_selected(request):
    if request.POST.get('priority') is not None:
        priority = True
    else:
        priority = False
    return priority


""" Checks whether NTNUI is hosting the event or not."""
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