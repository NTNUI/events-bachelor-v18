from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership
from .models import Event, EventDescription
from events import create_event, get_events


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


@login_required
def get_events(request):
    return get_events.get_events(request)


@login_required
def create_event(request):
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
