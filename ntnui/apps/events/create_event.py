from datetime import datetime

from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from events.models.event import Event, EventDescription
from groups.models import SportsGroup
from hs.models import MainBoardMembership


def create_event(request):
    """ Creates a new event for a given sports group. """

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Gets the data from the POST request.
    data = request.POST

    # Checks that the event has an Norwegian name and description text.
    norwegian_name = data.get('name_no')
    norwegian_description = data.get('description_text_no')

    if not (norwegian_name or norwegian_description):
        return get_json(400, _('Norwegian name and description is required.'))

    # Checks that the event has an English name and description text.
    english_name = data.get('name_en')
    english_description = data.get('description_text_no')

    if not (english_name or english_description):
        return get_json(400, _('English name and description is required.'))

    # Checks that the event has an valid start and end date.
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if start_date and end_date:
        # Start date is later than the end date.
        if start_date >= end_date:
            return get_json(400, _("Starting date cannot be later than end date."))
        # Start date is in the past.
        elif datetime.now() >= start_date.replace(tzinfo=None):
            return get_json(400, _("Starting date cannot be in the past."))
    else:
        # The event is lacking either start date or end date.
        return get_json(400, _('Start date and end date is required.'))

    # Creates the event.
    entry_created = create_and_validate_database_entry(request)

    # if success send event created
    if entry_created[0]:
        return JsonResponse({
            'id': entry_created[1].id,
            'message': _('New event successfully created!')},
            status=201)
        if entry_created[1] is not None:
            return get_json(400, entry_created[1])

    # if something goes wrong send faild to create event
    return get_json(400, _('Failed to create event!'))





def create_and_validate_database_entry(request):
    """ Tries to create an entry in the database for the event described in the POST message.
    The entry is validated, as well.
    """

    # Get the post data
    data = request.POST

    # get the value for prority
    priority = priority_is_selected(data.get('priority'))

    # checks if host is NTNUI, if so check that the user is member of the board
    if data.get('host') == 'NTNUI':
        if user_is_in_mainboard(request.user):
            return create_event_for_group(data, priority, True)
        else:
            return False, 'User is not in mainboard'

    # Checks that the sportGroup exists
    if SportsGroup.objects.filter(id=int(data.get('host'))).exists():

        # Get the active board
        active_board = SportsGroup.objects.get(id=int(data.get('host'))).active_board

        # Check that the active board is not None
        if active_board is not None:

            # Checks that the user got a position at the board
            if user_is_in_board(active_board, request.user):
                return create_event_for_group(data, priority, False)
            else:
                return False, get_json(400, _('User is not in '))"user is not in board"
        else:
            return False, "active_board is None"
    else:
        return False, "sportsGroup doesn't exist"


def create_event_for_group(data, priority, is_ntnui):
    """Creates a new event hosted by a group"""

    # If price is not given a value, price is set to 0
    price = data.get('price')
    if price == "":
        price = 0

    # if attendance_cap is "" its set to None
    attendance_cap = data.get('attendance_cap')
    if attendance_cap == "":
        attendance_cap = None

    registration_end_date = data.get('registration_end_date')
    if registration_end_date == "":
        registration_end_date = None;

    try:
        # create the events
        event = Event.objects.create(start_date=data.get('start_date'), end_date=data.get('end_date'), registration_end_date = registration_end_date,
                                     priority=priority, is_host_ntnui=is_ntnui, place=data.get('place'), attendance_cap=attendance_cap,
                                     price=price)

        if not is_ntnui:
            # Add the group as the host
            event.sports_groups.add(SportsGroup.objects.get(id=int(data.get('host'))))

        # Creates description and checks that it was created
        if create_description_for_event(event, data.get('description_text_no'), data.get('email_text_no'),
                                        data.get('name_no'), 'nb') and \
                create_description_for_event(event, data.get('description_text_en'), data.get('email_text_en'),
                                             data.get('name_en'), 'en'):
            return True, event
        return False, _('could not create description')

    # if something goes wrong return false and print error to console
    except Exception as e:
        print(e)
    return False, None


def priority_is_selected(priority):
    """ Checks whether the event is priorized or not."""
    if priority is not None:
        return True
    else:
        return False


def create_description_for_event(event, decription, email_text, name, lang):
    """Creates a description for a given event"""
    try:
        EventDescription.objects.create(name=name, description_text=decription, custom_email_text=email_text,
                                        language=lang, event=event)
        return True
    except Exception as e:
        print(e)
        return False


def user_is_in_mainboard(user):
    """Checks if user is in mainboard"""
    return MainBoardMembership.objects.filter(person_id=user).exists()


def user_is_in_board(board, user):
    """Checks if a given user is in board"""
    return board.president == user or board.vice_president == user or board.cashier == user





def get_json(code, message):
    """Returnes json with the given format"""
    return JsonResponse({
        'message': message},
        status=code)

