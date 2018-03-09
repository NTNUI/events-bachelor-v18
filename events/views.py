from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import gettext as _
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership
from .models import Event, EventDescription, EventRegistration, Category, SubEvent
from . import create_event, get_events


@login_required
def get_main_page(request):
    """Returns the main page for events"""

    # Used to find out if the create-event button shall be rendered or not
    can_create_event = user_can_create_event(request.user)

    # Get groups that are hosting events
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_main_page.html', {
        'can_create_event': can_create_event,
        'groups': groups,
    })


def get_event_details(request, id):
    sub_event_list = []
    # get the event from db
    event = Event.objects.get(id=int(id))
    # check that the event got one or more categories
    if Category.objects.filter(event=event).exists():
        categories = Category.objects.filter(event=event)
        # for every category do:
        for i in range(len(categories)):
            # get all the subevents for that category
            sub_event = SubEvent.objects.filter(category=categories[i])
            # add the category and map each sub_event to a dic
            sub_event_list.append((categories[i], list(map(lambda item: {
                'start_date': item.start_date,
                'end_date': item.end_date,
                'attends': item.attends(request.user),
                'name': str(item),
                'id': item.id
            }, sub_event))))

    event = {
        'name': event.name(),
        'description': event.description(),
        'start_date': event.start_date,
        'end_date': event.end_date,
        'cover_photo': event.cover_photo,
        'attends': event.attends(request.user),
        'id': event.id,
        'host': event.get_host(),
        'place': event.place
    }

    context = {
        "event": event,
        "sub_event_list": sub_event_list
    }

    return render(request, 'events/event_details.html', context)


@login_required
def get_events_request(request):
    return get_events.get_events(request)


@login_required
def create_event_request(request):
    """Creates a new event with the given data"""
    return create_event.create_event(request)


@login_required
def get_create_event_page(request):
    """Returns the page where events are created"""

    # Checks if a user can create an event
    groups = get_groups_user_can_create_events_for(request.user)

    return render(request, 'events/create_new_event.html',
                  {'groups': groups})


def user_can_create_event(user):
    """Checks to see if a user can create event of any kind"""

    # User is in MainBoard
    if user_is_in_mainboard(user):
        return True

    # Checks if the user is in any active board
    for board in Board.objects.filter(president=user) | \
                 Board.objects.filter(vice_president=user) | \
                 Board.objects.filter(cashier=user):

        # Checks that the board is active
        if SportsGroup.objects.filter(active_board=board):
            return True
    return False


def get_groups_user_can_create_events_for(user):
    """Finds the groups a user can create events for"""

    # Create an empty return list
    return_list = []

    # Adds NTNUI if member of hs
    if user_is_in_mainboard(user):
        return_list.append({'id': "NTNUI", 'name': 'NTNUI'})

    # Finds all the groups were the user is in the board
    for board in Board.objects.filter(president=user) | \
                 Board.objects.filter(vice_president=user) | \
                 Board.objects.filter(cashier=user):

        # Checks that the board is active
        for group in SportsGroup.objects.filter(active_board=board):
            return_list.append(group)

    return return_list


def user_is_in_mainboard(user):
    return MainBoardMembership.objects.filter(person_id=user).exists()


"""Checks if a given user is in board"""


def user_is_in_board(board, user):
    return board.president == user or board.vice_president == user or board.cashier == user


"""Checks that a description is not empyt"""


def event_has_description_and_name(description, name):
    if description is None or description.replace(' ', '') == "":
        return False, 'Event must have description'
    elif name is None or name.replace(' ', '') == "":
        return False, _('Event must have a name')
    return True, None


"""Returnes json with the given format"""


def get_json(code, message):
    return JsonResponse({
        'message': message},
        status=code)


@login_required
def event_add_attendance_event(request):
    """Adds attendance to the given event for the given user"""
    if request.POST:
        id = request.POST.get('id')
        event = Event.objects.get(id=int(id))
        # Checks that the user is not already attending
        if not EventRegistration.objects.filter(event=event, attendee=request.user).exists():
            try:
                # Try to create a enry
                EventRegistration.objects.create(event=event, attendee=request.user, registration_time=datetime.now())
                return get_json(201, 'You are now attending this event')
            except:
                return get_json(400, 'Could not add you to this event')
        return get_json(400, 'You are already attending this event')
    return get_json(400, 'Request must be post')


@login_required
def event_remove_attendance_event(request):
    """Remove the user from attending the given event """
    if request.POST:
        try:
            id = request.POST.get('id')
            if EventRegistration.objects.filter(event__id=int(id), attendee=request.user).exists():
                registration = EventRegistration.objects.get(event__id=int(id), attendee=request.user)
                registration.delete()
                return get_json(201, 'Success')
            return get_json(400, 'Attendance dose not exists')
        except:
            return get_json(400, 'Could not remove attendence')
    return get_json(400, 'request is not post')


@login_required
def event_add_attendance_subevent(request):
    """Add a user to the given subevent"""
    if request.POST:
        try:
            id = request.POST.get('id')
            subevent = SubEvent.objects.get(id=int(id))
            subevent.attending_members.add(request.user)
            subevent.save()
            return get_json(201, 'Success')
        except:
            return get_json(400, 'Could not join event')
    return get_json(400, 'request is not post')


@login_required
def event_remove_attendance_subevent(request):
    """Removes the given user from the given subevent"""
    if request.POST:
        try:
            id = request.POST.get('id')
            subevent = SubEvent.objects.get(id=int(id))
            # find the subevent and remove the user from that sub event
            subevent.attending_members.remove(request.user)
            subevent.save()
            return get_json(201, 'Success')
        except:
            return get_json(400, 'Could not remove attendence')
    return get_json(400, 'request is not post')
