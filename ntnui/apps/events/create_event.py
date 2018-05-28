from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from events.models.event import Event, EventDescription
from groups.models import SportsGroup

from .views import get_json, is_user_in_board, is_user_in_main_board


@login_required
def create_event_request(request):
    """ Creates a new event for a given sports group. """

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, _('Request must be POST.'))

    # Gets the user and the POST request's data.

    data = request.POST
    user = request.user

    # Checks that the required fields for an event is valid.
    error_message = validate_event_data(data)
    if error_message:
        return get_json(400, _(error_message))

    # Creates the event.
    event, event_created, error_message = create_event(data, user)
    if event_created:
        return JsonResponse({'id': event.id, 'message': _('New event successfully created!')}, status=201)
    else:
        return get_json(400, _(error_message))


def validate_event_data(data):
    """ Checks that the event's start and end date is valid, and that it has
        an English and Norwegian name and description, and its start and end date. """

    # Gets the required data for creating an event.
    norwegian_name = data.get('name_no')
    norwegian_description = data.get('description_text_no')
    english_name = data.get('name_en')
    english_description = data.get('description_text_no')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    location = data.get('place')
    host = data.get('host')

    # Checks that the event has an Norwegian name and description text.
    if not (norwegian_name and norwegian_description):
        return 'Norwegian name and description is required.'

    # Checks that the event has an English name and description text.
    if not (english_name and english_description):
        return 'English name and description is required.'

    # Checks that the event has a location.
    if not location:
        return 'Location is required.'

    # Checks that the event has a host.
    if not host:
        return 'Host is required.'

    # The event's data is validated.
    return None


def create_event(data, user):
    """ Creates the event, either as NTNUI or a sports group. """

    # Gets the required data.
    host = data.get('host')

    # NTNUI is the host of the event.
    if host == 'NTNUI':

        # Checks that the user got a position in the main board, and creates the event.
        if is_user_in_main_board(user):
            return create_event_for_group(data, True)
        else:
            return None, False, 'Cannot create an event for NTNUI without being part of the main board.'

    # A sports group is the host of the event.
    else:

        # Checks that the sports group exists.
        sports_group = get_sports_group_by_id(host)
        if not sports_group:
            return None, False, 'Sports group does not exist.'

        # Checks that the sports group has an active board.
        active_board = sports_group.active_board
        if not active_board:
            return None, False, 'Active board does not exist.'

        # Checks that the user got a position in the group's board, and creates the event.
        if is_user_in_board(active_board, user):
            return create_event_for_group(data, False)
        else:
            return None, False, 'Cannot create an event for an sports group without being part of the group board.'


def create_event_for_group(data, is_host_ntnui):
    """ Creates a new event hosted by a sports group. """

    # Sets the event's price to 0 if it is not set.
    price = data.get('price', 0)

    # Sets the event's attendance cap to None if it is not set.
    attendance_cap = data.get('attendance_cap', None)
    if attendance_cap == "":
        attendance_cap = None

    # Sets the event's registration end date to None if it is not set.
    registration_end_date = data.get('registration_end_date', None)
    if registration_end_date == "":
        registration_end_date = None

    try:
        # Creates the event.
        event = Event.objects.create(start_date=data.get('start_date') + '+0000',
                                     end_date=data.get('end_date') + '+0000',
                                     place=data.get('place'), price=price,
                                     registration_end_date=registration_end_date,
                                     is_host_ntnui=is_host_ntnui, attendance_cap=attendance_cap)

        # Sets the event's host, if the host is not NTNUI.
        if not is_host_ntnui:
            event.sports_groups.add(get_sports_group_by_id(data.get('host')))

        # Creates the Norwegian event description.
        create_event_description(
            event, data.get('name_no'), data.get('description_text_no'), data.get('email_text_no'), 'nb')

        # Creates the English event description.
        create_event_description(
            event, data.get('name_en'), data.get('description_text_en'), data.get('email_text_en'), 'en')

        # The event were successfully created.
        return event, True, None

    # Catch exceptions.
    except Exception as e:
        print(e)
        return None, False, 'Failed to create the event.'


def create_event_description(event, name, description, email_text, language):
    """ Creates an event description. """

    # Creates an event description.
    try:
        EventDescription.objects.create(
            event=event, name=name, description_text=description, custom_email_text=email_text, language=language)
        return True

    # Catch exceptions.
    except Exception as e:
        print(e)
        return False


def get_sports_group_by_id(sports_group_id):
    """ Gets the sports group if it exists. """

    # Get the sports group.
    try:
        return SportsGroup.objects.get(id=sports_group_id)

    # Catch exceptions.
    except SportsGroup.DoesNotExist:
        return None
    except Exception as e:
        print(e)
        return None
