from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _
from events.models.category import Category, CategoryDescription
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.sub_event import (SubEvent, SubEventDescription,
                                     SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership


def get_remove_attendance_page(request, token):
    """ Renders the remove attendance page. """

    return render(request, 'events/remove_attendance.html', {'token': token})


def get_delete_event_page(request):
    """ Renders the event main page after deleting an event. """

    return get_events_main_page(request)


def get_events_main_page(request):
    """ Renders the events' main page. """

    # Checks if the user is eligible to create events.
    if request.user.is_authenticated:
        can_create_event = can_user_create_event(request.user)
    else:
        can_create_event = False

    # Get groups that are hosting events.
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_main_page.html', {'can_create_event': can_create_event,
                                                            'groups': groups})


@login_required
def get_create_event_page(request):
    """ Renders the page where events are created. """

    # Checks if a user can create an event.
    groups = get_groups_user_can_create_events_for(request.user)
    
    return render(request, 'events/create_new_event.html', {'groups': groups})

  
def get_remove_attendance_page(request, token):
    """Returnes the remove attend page"""
    return render(request, 'events/remove_attendance.html', {'token': token})


def get_attending_events_page(request):
    """ Renders the page with the events which the user attends. """

    # Used to find out if the create-event button shall be rendered or not
    if request.user.is_authenticated:
        can_create_event = can_user_create_event(request.user)
    else:
        can_create_event = False

    # Get groups that are hosting events.
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_attending_page.html', {'can_create_event': can_create_event,
                                                                 'groups': groups})


def get_event_details_page(request, event_id):
    """ Renders the event detail page for a given event. """

    sub_event_list = []
    event = get_event_by_id(event_id)

    # Checks if the event has categories.
    if Category.objects.filter(event=event).exists():
        categories = Category.objects.filter(event=event)

        # Gets all the category's sub-events.
        # Adds the category and maps each of the category's sub-events to a dictionary.
        for category in categories:
            sub_events = SubEvent.objects.filter(category=category)
            sub_event_list.append(
                (category, list(map(lambda sub_event: get_sub_event_dict(sub_event, request.user), sub_events))))

    if request.user.is_authenticated:

        # Checks if the user attends the event or is on its waiting list, and if the user is eligible to create events.
        attends = event.is_user_enrolled(request.user)
        can_create_event = can_user_create_event(request.user)
        is_user_on_waiting_list = event.is_user_on_waiting_list(request.user)

        # Checks if the user can edit and delete the event.
        if user_can_edit_and_delete_event(event, request.user):
            can_edit_and_delete_event = True
        else:
            can_edit_and_delete_event = False

    # Sets the values for users who are not logged in and guests.
    else:
        attends = False
        is_user_on_waiting_list = False
        can_create_event = False
        can_edit_and_delete_event = False

    # Creates a dictionary for the event.
    event = {
        'name': event.name(),
        'description': event.description(),
        'start_date': event.start_date,
        'end_date': event.end_date,
        'cover_photo': event.cover_photo,
        'attends': attends,
        'id': event.id,
        'waiting_list': event.is_attendance_cap_exceeded(),
        'is_user_on_waiting_list': is_user_on_waiting_list,
        'number_of_participants': len(event.get_attendee_list()),
        'attendance_cap': event.attendance_cap,
        'is_registration_ended': event.is_registration_ended(),
        'price': event.price,
        'registration_end_date': event.registration_end_date,
        'payment_required': event.is_payment_event(),
        'host': event.get_host(),
        'place': event.place,
        'language': translation.get_language
    }

    # Creates a dictionary for the page requested.
    context = {
        "event": event,
        "is_authenticated": request.user.is_authenticated,
        "sub_event_list": sub_event_list,
        'number_of_sub_events': len(sub_event_list),
        'can_create_event': can_create_event,
        'can_edit_and_delete_event': can_edit_and_delete_event,
        "STRIPE_KEY": settings.STRIPE_PUBLIC_KEY
    }

    return render(request, 'events/event_details.html', context)


def get_event_attendees_page(request, event_id):
    """ Renders the page where the attendees for the event or the event's sub-events are shown."""

    # Gets the event.
    event = get_event_by_id(event_id)

    # Checks if the event has sub-events.
    if not len(get_sub_events(event)) > 0:

        # The event does not have sub-events.
        sub_events_exist = False

        # Gets the event's attendees.
        attendees = []
        for attendee in event.get_attendee_list():
            attendees.append(str(attendee))

        context = {
            'sub_events_exist': sub_events_exist,
            'event': event,
            'attendees_list': attendees,
        }

    else:
        # The event has sub-events.
        sub_events_exist = True

        # Gets the event's sub-events.
        sub_events = get_sub_events(event)

        # Gets the attendees from each sub-event.
        sub_events_attendees_and_names_list = []
        for sub_event in sub_events:
            attendees = []
            for attendee in sub_event.get_attendee_list():
                attendees.append(str(attendee))

            # Adds the list of attendees together with the sub-event's name.
            sub_events_attendees_and_names_list.append((attendees, sub_event.name()))

        context = {
            'sub_events_exist': sub_events_exist,
            'event': event,
            'sub_events_attendees_and_name_list': sub_events_attendees_and_names_list,
        }

    return render(request, 'events/event_attendees_page.html', context)


def get_edit_event_page(request, event_id):
    """ Renders the edit event page for a given event. """

    # Gets the event.
    event = get_event_by_id(event_id)

    # Gets the event's data.
    price = event.price
    attendance_cap = event.attendance_cap
    groups = get_groups_user_can_create_events_for(request.user)
    event_description_no = EventDescription.objects.get(event=event, language='nb')
    event_description_en = EventDescription.objects.get(event=event, language='en')

    # Converts dates to a format that can be put as value in inputtype datetimelocal html form.
    event_start_date = event.start_date
    event_end_date = event.end_date
    start_date = '{:%Y-%m-%dT%H:%M}'.format(event_start_date)
    end_date = '{:%Y-%m-%dT%H:%M}'.format(event_end_date)

    # Checks if the event has a registration_end_date, and converts it if it exists.
    registration_end_date = ""
    if event.registration_end_date != "" and event.registration_end_date is not None:
        registration_end_date = '{:%Y-%m-%dT%H:%M}'.format(event.registration_end_date)

    # Creates a dictionary for the event.
    event = {
        'name_no': event_description_no.name,
        'name_en': event_description_en.name,
        'description_text_no': event_description_no.description_text,
        'description_text_en': event_description_en.description_text,
        'email_text_no': event_description_no.custom_email_text,
        'email_text_en': event_description_en.custom_email_text,

        'start_date': start_date,
        'end_date': end_date,
        'id': event.id,
        'attendance_cap': attendance_cap,
        'registration_end_date': registration_end_date,
        'price': price,
        'host': event.get_host(),
        'place': event.place,
        'groups': groups
    }

    context = {
        "event": event,
    }

    return render(request, 'events/edit_event_page.html', context)


""" Help functions for the functions explicitly in this file. """


def can_user_create_event(user):
    """ Checks if the user can create events. """

    # Checks if the user is a member of the main board.
    if is_user_in_main_board(user):
        return True

    # Checks if the user is in a member of any active boards.
    for board in (Board.objects.filter(Q(president=user) | Q(vice_president=user) | Q(cashier=user))):

        # Checks that the board which the user is a member of is active.
        if SportsGroup.objects.filter(active_board=board).exists():
            return True

    # The user is not eligible to create events.
    return False


def user_can_edit_and_delete_event(event, user):
    """ Checks if the user can edit and delete a given event. """

    # Checks if the user is in NTNUI's main board.
    if is_user_in_main_board(user):
        return True

    # Gets the event's hosts.
    event_hosts = []
    for group in event.sports_groups.all():
        event_hosts.append(group)

    # Checks if the user is in a board which is eligible to edit and delete the event.
    user_boards = get_groups_user_can_create_events_for(user)
    for board in user_boards:
        if board in event_hosts:
            return True

    # The user is not eligible to edit and delete the event.
    return False


def get_groups_user_can_create_events_for(user):
    """ Gets a user, and checks which groups the user is eligible to create events for. """

    # Create an empty return list
    return_list = []

    # Adds NTNUI if member of hs
    if is_user_in_main_board(user):
        return_list.append({'id': "NTNUI", 'name': 'NTNUI'})

    # Finds all the groups were the user is in the board
    for board in (Board.objects.filter(president=user) | Board.objects.filter(vice_president=user) |
                  Board.objects.filter(cashier=user)):

        # Checks that the board is active
        for group in SportsGroup.objects.filter(active_board=board):
            return_list.append(group)

    # List with the groups which the user can create events for.
    return return_list


def get_event(event_id):
    """ Creates a dictionary of a given event. """

    # Checks that the event exists.
    if not Event.objects.filter(id=int(event_id)).exists():
        return get_json(400, "Event with id: " + event_id + " does not exist.")

    # Gets the event.
    event = get_event_by_id(event_id)

    # Checks if the event got categories.
    categories_list = []
    if Category.objects.filter(event=event).exists():
        categories = Category.objects.filter(event=event).values()

        # Get the each category's descriptions and sub-events.
        for i in range(len(categories)):
            categories[i]['sub-events'] = list(SubEvent.objects.filter(category__id=categories[i]['id']).values())
            categories[i]['descriptions'] = list(
                CategoryDescription.objects.filter(category__id=categories[i]['id']).values())

            # Transform each sub-event's to the right format.
            for j in range(len(categories[i]['sub-events'])):

                # Adds sub-event to the category's list of sub-events.
                sub_event = categories[i]['sub-events'][j]

                # Fixes the start-date's and end-date's format.
                sub_event['start_date'] = '{:%Y-%m-%dT%H:%M}'.format(sub_event['start_date'])
                sub_event['end_date'] = '{:%Y-%m-%dT%H:%M}'.format(sub_event['end_date'])

                # Adds the sub-event's descriptions.
                sub_event['descriptions'] = list(
                    SubEventDescription.objects.filter(sub_event__id=sub_event['id']).values())

                # Adds the registration_end_date and fixes its format.
                if sub_event['registration_end_date'] is not None and sub_event['registration_end_date'] != "":
                    sub_event['registration_end_date'] = '{:%Y-%m-%dT%H:%M}'.format(sub_event['registration_end_date'])

            # Adds the category to the list of categories.
            categories_list.append(categories[i])

    # Returns the event as a dictionary.
    return JsonResponse({
        'id': event.id,
        'name': event.name(),
        'place': event.place,
        'descriptions': list(EventDescription.objects.filter(event=event).values()),
        'start_date': event.start_date,
        'end_date': event.end_date,
        'priority': event.priority,
        'price': event.price,
        'host': event.get_host(),
        'cover_photo': str(event.cover_photo),
        'categories': list(categories_list),
    })


def get_sub_event(sub_event_id):
    """ Creates a dictionary of a given sub-event. """

    # Checks that the sub-event exists.
    if SubEvent.objects.filter(id=int(sub_event_id)).exists():

        # Creates dictionary for the sub-event.
        sub_event = SubEvent.objects.get(id=int(sub_event_id))
        sub_event_dict = model_to_dict(sub_event)
        sub_event_dict["name"] = sub_event.name()
        sub_event_dict["host"] = sub_event.get_host()

        # Returns the created dictionary.
        return JsonResponse(sub_event_dict)

    # No sub-event matches the given sub-event ID.
    return get_json(400, "Sub-event with id: " + sub_event_id + " does not exist.")


def get_sub_event_dict(sub_event, user):
    """ Creates a dictionary for a sub-event, including whether the attends the sub-event user."""

    # Checks if the user attends the sub-event, or is on its waiting list.
    if user.is_authenticated:
        attends = sub_event.is_user_enrolled(user)
        is_user_on_waiting_list = sub_event.is_user_on_waiting_list(user)
    else:
        # User is not logged in.
        attends = False
        is_user_on_waiting_list = False

    # Returns the created dictionary for the sub-event.
    return {
        'start_date': sub_event.start_date,
        'end_date': sub_event.end_date,
        'attends': attends,
        'waiting_list': sub_event.is_attendance_cap_exceeded(),
        'is_user_on_waiting_list': is_user_on_waiting_list,
        'number_of_participants': len(sub_event.get_attendee_list()),
        'attendance_cap': sub_event.attendance_cap,
        'is_registration_ended': sub_event.is_registration_ended(),
        'registration_end_date': sub_event.registration_end_date,
        'name': str(sub_event),
        'price': sub_event.price,
        'payment_required': sub_event.is_payment_event(),
        'id': sub_event.id
    }


""" Functions which is used in multiple files. """


def get_json(code, message):
    """ Returns JSON with the given format. """

    return JsonResponse({'message': message}, status=code)


def get_event_by_id(event_id):
    """ Gets the event which the event ID is associated with. """

    try:
        return Event.objects.get(id=event_id)
    except Event.DoesNotExist:
        return get_json(404, _("Event doesn't exist."))


def get_sub_event_by_id(sub_event_id):
    """ Gets the sub-event which the sub-event ID is associated with. """

    try:
        return SubEvent.objects.get(id=sub_event_id)
    except SubEvent.DoesNotExist:
        return get_json(404, _("Sub-event doesn't exist."))


def get_sub_events(event):
    """ Gets a given event's sub-events. """

    return SubEvent.objects.filter(category__in=Category.objects.filter(event=event))


def is_user_in_main_board(user):
    """ Checks if the user is a member of the main board. """

    return MainBoardMembership.objects.filter(person_id=user).exists()


def is_user_in_board(board, user):
    """ Checks if the user is a member of the board. """

    return board.president == user or board.vice_president == user or board.cashier == user
