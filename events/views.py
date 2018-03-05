from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.translation import gettext as _
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership
from django.core.paginator import Paginator
from .models import Event, EventDescription
from django.core import serializers
from django.db.models import Q
from django.utils import translation


"""Returns the main page for events"""


@login_required
def events(request):
    # Used to find out if the create-event button shall be rendered or not
    can_create_event = user_can_create_event(request.user)
    groups = get_groups_currently_hosting_events()

    return render(request, 'events/events_main_page.html', {
        'can_create_event': can_create_event,
        'groups': groups,
    })


def get_groups_currently_hosting_events():
    groups_hosting_events = []
    event_hosts = SportsGroup.objects.filter(event__in   = Event.objects.all()).distinct()
    return event_hosts



@login_required
def get_events(request):
    if (request.GET):
        page = request.GET.get('page', 1)

        # get filtered events
        events = get_filtered_events(request)

        p = Paginator(events, 10)

        events = get_event_json(p.page(page))

        return JsonResponse({
            'events': events,
            'page_number': page,
            'page_count': p.num_pages}
        )
    return JsonResponse({
        'messsage': 'must be get'
    }, 404)


"""Returnes all the events that fits the order_by, search and filter_by"""


def get_filtered_events(request):
    sort_by = request.GET.get('sort_by')
    search = request.GET.get('search')
    filter_host = request.GET.get('fiter_host', [])

    # Checks if search have a value
    if search is not None and search != '':
        # serach for the word in descriptions and name
        events = Event.objects.filter(Q(eventdescription__language=translation.get_language()) &
                                      (Q(eventdescription__name__icontains=search) | Q(
            eventdescription__description_text__icontains=search)))
    else:
        # if not search return all event objects
        events = Event.objects.filter(eventdescription__language=translation.get_language())




    # Allowed order_by
    allowed_sort_by = ['name', 'description', 'start_date', 'end_date']
    # checks that order_by have a value and that it is in the allowed_order_by
    if sort_by is not None and (sort_by in allowed_sort_by or sort_by[1:] in allowed_sort_by):
        # checks the first character
        type = ''
        if sort_by[0] == '-':
            type = '-'
            order_by = sort_by[1:]

        # if the sort by is not in the event table we need to find the filed by merging
        if sort_by == 'name':
            sort_by = type + 'eventdescription__name'
        elif sort_by == 'description':
            sort_by = type + 'eventdescription__description_text'

        # return the result
        return events.order_by(sort_by, 'priority', 'start_date')
    else:
        # return the result
        return  events.order_by('-priority', 'start_date')



"""Returnes list of dic of event"""


def get_event_json(events):
    return_events = []
    for event in events:
        return_events.append({
            'name': str(event.name()),
            'description': str(event.description()),
            'start_date': str(event.start_date),
            'end_date': str(event.end_date),
            'priority': str(event.priority),
            'host': str(event.get_host())
        })
    return return_events


"""Checks to see if a user can create event of any kind"""


def user_can_create_event(user):
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


"""Returns the page where events are created"""


@login_required
def get_create_event_page(request):
    groups = get_groups_user_can_create_events_for(request.user)
    return render(request, 'events/create_new_event.html',
                  {'groups': groups})


"""Finds the groups a user can create events for"""


def get_groups_user_can_create_events_for(user):
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


"""Creates a new event with the given data"""


@login_required
def create_event(request):
    print(request)
    if request.method == "POST":

        # Get the data from the post
        data = request.POST

        # checks that the description and name are not empty
        has_english_description = event_has_description_and_name(data.get('description_text_en'), data.get('name_en'))
        if not has_english_description[0]:
            return get_json(400, has_english_description[1])

        has_norwegian_description = event_has_description_and_name(data.get('description_text_no'), data.get('name_no'))
        if not has_norwegian_description[0]:
            return get_json(400, has_norwegian_description[1])

        # Tries to create the event
        entry_created = create_and_validate_database_entry(request)

        # if succsess send event created
        if entry_created[0]:
            return get_json(201, _('New event successfully created!'))
        if entry_created[1] is not None:
            return get_json(400, entry_created[1])

    # if something goes wrong send faild to create event
    return get_json(400, _('Failed to create event!'))


""" Tries to create an entry in the database for the event described in the POST message.
The entry is validated, as well.
"""


def create_and_validate_database_entry(request):
    # Get the post data
    data = request.POST

    # get the value for prority
    priority = priority_is_selected(data.get('priority'))

    # checks if host is NTNUI, if so check that the user is member of the board
    if data.get('host') == 'NTNUI' and user_is_in_mainboard(request.user):
        return create_event_for_group(data, priority, True)

    # Checks that the sportGroup exists
    if SportsGroup.objects.filter(id=int(data.get('host'))).exists():

        # Get the active board
        active_board = SportsGroup.objects.get(id=int(data.get('host'))).active_board

        # Check that the active board is not None
        if active_board is not None:

            # Checks that the user got a position at the board
            if user_is_in_board(active_board, request.user):
                return create_event_for_group(data, priority, False)


"""Creates a new event hosted by a group"""


def create_event_for_group(data, priority, is_ntnui):
    try:
        # create the events
        event = Event.objects.create(start_date=data.get('start_date'), end_date=data.get('end_date'),
                                     priority=priority, is_host_ntnui=is_ntnui)

        if not is_ntnui:
            # Add the group as the host
            event.sports_groups.add(SportsGroup.objects.get(id=int(data.get('host'))))

        # Creates description and checks that it was created
        if create_description_for_event(event, data.get('description_text_no'), data.get('name_no'), 'nb') and \
                create_description_for_event(event, data.get('description_text_en'), data.get('name_en'), 'en'):
            return True, None
        return False, _('could not create description')

    # if something goes worng return false and print error to console
    except Exception as e:
        print(e)
    return False, None


""" Checks whether the event is priorized or not."""


def priority_is_selected(priority):
    if priority is not None:
        return True
    else:
        return False


"""Creates a description for a given event"""


def create_description_for_event(event, decription, name, lang):
    try:
        EventDescription.objects.create(name=name, description_text=decription, language=lang, event=event)
        return True
    except Exception as e:
        print(e)
        return False


"""Checks if user is in mainboard"""


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
