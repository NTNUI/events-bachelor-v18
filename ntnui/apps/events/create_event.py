from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from groups.models import SportsGroup
from hs.models import MainBoardMembership

from events.models import Event, EventDescription


def create_event(request):
    """Creates a new event for a given sports group"""
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
            return (False, 'User is not in mainboard')

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
                return (False, "user is not in board")
        else:
            return (False, "active_board is None")
    else:
        return (False, "sportsGroup doesn't exist")



def create_event_for_group(data, priority, is_ntnui):
    """Creates a new event hosted by a group"""
    try:
        # create the events
        event = Event.objects.create(start_date=data.get('start_date'), end_date=data.get('end_date'),
                                     priority=priority, is_host_ntnui=is_ntnui)

        if not is_ntnui:
            # Add the group as the host
            event.sports_groups.add(SportsGroup.objects.get(id=int(data.get('host'))))

        # Creates description and checks that it was created
        if create_description_for_event(event, data.get('description_text_no'), data.get('email_text_no'), data.get('name_no'), 'nb') and \
                create_description_for_event(event, data.get('description_text_en'), data.get('email_text_en'), data.get('name_en'), 'en'):
            return True, None
        return False, _('could not create description')

    # if something goes worng return false and print error to console
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
        EventDescription.objects.create(name=name, description_text=decription, custom_email_text=email_text, language=lang, event=event)
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


def event_has_description_and_name(description, name):
    """Checks that a description is not empyt"""
    if description is None or description.replace(' ', '') == "":
        return False, 'Event must have description'
    elif name is None or name.replace(' ', '') == "":
        return False, _('Event must have a name')
    return True, None


def get_json(code, message):
    """Returnes json with the given format"""
    return JsonResponse({
        'message': message},
        status=code)
