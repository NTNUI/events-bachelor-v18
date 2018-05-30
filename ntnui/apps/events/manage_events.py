from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.translation import gettext as _

from events.models.category import Category, CategoryDescription
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.sub_event import (SubEvent, SubEventDescription,
                                     SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)

from .views import (get_json, get_groups_user_can_create_events_for)


@login_required
def create_category_request(request):
    """ Creates a new category with the provided data. """

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    data = request.POST

    # Gets the event
    event = Event.objects.get(id=int(data.get('event')))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(event, request.user):
        return get_json(400, 'You do not have the authority to create the category.')

    # Gets the category's name in Norwegian and English.
    name_nb = data.get('name_nb')
    name_en = data.get('name_en')

    # Creates the category for the
    category = Category.objects.create(event=event)

    # Creates the category's Norwegian and English description, consisting of its name.
    CategoryDescription.objects.create(category=category, name=name_nb, language='nb')
    CategoryDescription.objects.create(category=category, name=name_en, language='en')

    # Returns the category's ID and a JSON success response.
    return JsonResponse({'id': category.id, 'message': _('The category is successfully created!')}, status=201)


@login_required
def edit_category_request(request):
    """ Edits an existing category with the provided data. """

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    data = request.POST

    # Checks if the category exists
    if not Category.objects.filter(id=int(data.get('id'))).exists():
        return get_json(400, "Category dose not exist")

    # Gets the category which is edited.
    category = Category.objects.get(id=int(data.get('id')))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(category.event, request.user):
        return get_json(400, 'You do not have the authority to edit the category.')

    # Gets the new category name in Norwegian and English.
    category_name_nb = data.get('name_nb')
    category_name_en = data.get('name_en')

    # Edits the category's Norwegian and English name.
    category_description_nb = CategoryDescription.objects.get(category=category, language='nb')
    category_description_en = CategoryDescription.objects.get(category=category, language='en')
    category_description_nb.name = category_name_nb
    category_description_en.name = category_name_en
    category_description_nb.save()
    category_description_en.save()

    # Returns the category's ID and a JSON success response.
    return JsonResponse({'id': data.get('id'), 'message': 'Edit category successful!'}, status=200)


@login_required
def delete_category_request(request):
    """ Deletes a given category. """

    # Get the category.
    category = Category.objects.get(id=int(request.POST['id']))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(category.event, request.user):
        return get_json(400, 'You do not have the authority to delete the category.')

    return delete_category(category)


def delete_category(category):
    """ Help-function for deleting a category. """

    # Gets the category's descriptions.
    category_description_nb = CategoryDescription.objects.get(category=category, language='nb')
    category_description_en = CategoryDescription.objects.get(category=category, language='en')

    # Gets the category's sub-event and deletes them.
    if SubEvent.objects.filter(category=category).exists():
        sub_events = SubEvent.objects.filter(category=category)
        for sub_event in sub_events:
            delete_sub_event(sub_event)

    # Deletes the category and its descriptions.
    category_description_nb.delete()
    category_description_en.delete()
    category.delete()

    # Returns a JSON success response.
    return get_json(200, "Category deleted!")


@login_required
def create_sub_event_request(request):
    """ Creates a new event with the provided data. """

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    data = request.POST

    # Gets the event

    if not data.get('event'):
        return get_json(400, 'Must include event id')

    event = Event.objects.get(id=int(data.get('event')))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(event, request.user):
        return get_json(400, 'You do not have the authority to create the sub-event.')

    # Gets the category's name and description text in Norwegian and English.
    name_nb = data.get('name_nb')
    name_en = data.get('name_en')
    email_text_nb = data.get('email_nb')
    email_text_en = data.get('email_en')

    # Sets the price to 0 if it is not set.
    price = data.get('price', 0)
    if not price:
        price = 0
    else:
        price = int(price)

    # Sets the attendance_cap to None if it is not set.
    attendance_cap = data.get('attendance_cap', None)
    if not attendance_cap:
        attendance_cap = None

    # Sets the registration_end_date to None if it is not set.
    registration_end_date = data.get('registration_end_date')
    if not registration_end_date:
        registration_end_date = None
    else:
        registration_end_date = registration_end_date + '+0000'

    category_id = data.get('category')

    # The sub-event does not have an existing category.
    if not category_id:

        # If the event does not have a 'Non categorized' category, one gets created for the sub-event.
        if not Category.objects.filter(event=event, categorydescription__name='Non categorized').exists():
            category = Category.objects.create(event=event)
            CategoryDescription.objects.create(category=category, name='Ikke kategorisert', language='nb')
            CategoryDescription.objects.create(category=category, name='Non categorized', language='en')

        # Finds the existing 'Non categorized' category and uses it for the sub-event.
        else:
            category = Category.objects.filter(event=event, categorydescription__name='Non categorized')[0]

    # Sets the sub-event's existing category.
    else:
        category = Category.objects.get(id=int(category_id))

    # Validates the input for the sub-event.
    sub_event = SubEvent.objects.create(start_date=data.get('start_date') + '+0000',
                                        end_date=data.get('end_date') + '+0000',
                                        price=price,
                                        registration_end_date=registration_end_date,
                                        attendance_cap=attendance_cap,
                                        category=category)

    # Validates the input for the sub-event's description.
    SubEventDescription.objects.create(sub_event=sub_event, name=name_nb, custom_email_text=email_text_nb,
                                       language='nb')
    SubEventDescription.objects.create(sub_event=sub_event, name=name_en, custom_email_text=email_text_en,
                                       language='en')

    # Returns the sub-event's ID and a JSON success response.
    return JsonResponse({'id': sub_event.id, 'message': _('The sub-event is successfully created!')}, status=201)

@login_required
def edit_sub_event_request(request):
    """ Edits an existing sub-event with the provided data. """

    # Checks that the request is POST.
    if not request.method == 'POST':
        return get_json(400, 'Request must be POST.')

    data = request.POST

    # Gets the event
    sub_event = SubEvent.objects.get(id=int(data.get('id')))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(sub_event, request.user):
        return get_json(400, 'You do not have the right to edit the sub-event.')

    # Gets the new input for the sub-event.
    name_nb = data.get('name_nb')
    name_en = data.get('name_en')
    email_text_nb = data.get('email_nb')
    email_text_en = data.get('email_en')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    registration_end_date = data.get('registration_end_date')
    attendance_cap = data.get('attendance_cap')
    price = data.get('price')
    category = data.get('category')

    # Gets the sub-event which is edited.
    sub_event = SubEvent.objects.get(id=int(data.get('id')))

    # Checks if the sub-event has been given a category, otherwise sets it to 'Non categorized' category.
    if category:
        sub_event.category = Category.objects.get(id=int(category))
    else:
        sub_event.category = Category.objects.filter(
            categorydescription__name='Ikke kategorisert', event__id=int(data.get('event')))[0]

    # Sets the start and end date.
    sub_event.start_date = start_date + '+0000'
    sub_event.end_date = end_date + '+0000'

    # Sets the registration_end_date to None if it is not set, otherwise to the given value.
    if not registration_end_date:
        sub_event.registration_end_date = None
    else:
        sub_event.registration_end_date = registration_end_date + '+0000'

    # Sets the attendance_cap to None if it is not set, otherwise to the given value.
    if not attendance_cap:
        sub_event.attendance_cap = None

    # Sets the price to None if it is not set, otherwise to the given value.
    if not price:
        sub_event.price = 0
    else:
        sub_event.price = int(price)

    # Saves the updated sub-event.
    sub_event.save()

    # Gets the new input for the sub-event's description.
    sub_event_description_nb = SubEventDescription.objects.get(sub_event=sub_event, language='nb')
    sub_event_description_en = SubEventDescription.objects.get(sub_event=sub_event, language='en')
    sub_event_description_nb.name = name_nb
    sub_event_description_en.name = name_en

    # Sets the email_text to None if it is not set, otherwise to the given value.
    if email_text_nb == '':
        sub_event_description_nb.custom_email_text = None
    else:
        sub_event_description_nb.custom_email_text = email_text_nb
    if email_text_en == '':
        sub_event_description_en.custom_email_text = None
    else:
        sub_event_description_en.custom_email_text = email_text_en

    # Saves the updated sub-event's description.
    sub_event_description_nb.save()
    sub_event_description_en.save()

    # Returns JSON success response.
    return get_json(200, 'Edit sub-event successful!')


@login_required
def delete_sub_event_request(request):
    """ Deletes a given sub-event. """

    # Get the sub-event
    sub_event = SubEvent.objects.get(id=int(request.POST['id']))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(sub_event, request.user):
        return get_json(400, 'You do not have the right to deleting the sub-event.')

    return delete_sub_event(sub_event)


def delete_sub_event(sub_event):
    """ Help-function for deleting a sub-event. """

    # Gets the sub-event's descriptions.
    sub_event_description_nb = SubEventDescription.objects.get(sub_event=sub_event, language='nb')
    sub_event_description_en = SubEventDescription.objects.get(sub_event=sub_event, language='en')

    # Gets the sub-event's user and guest registrations.
    sub_event_registrations = SubEventRegistration.objects.filter(sub_event=sub_event)
    sub_event_waiting_lists = SubEventWaitingList.objects.filter(sub_event=sub_event)
    sub_event_guest_registrations = SubEventGuestRegistration.objects.filter(sub_event=sub_event)
    sub_event_guest_waiting_lists = SubEventGuestWaitingList.objects.filter(sub_event=sub_event)

    # Deletes the sub-event's registrations of users.
    if sub_event_registrations:
        for sub_event_registration in sub_event_registrations:
            sub_event_registration.delete()

    # Deletes the sub-event's registrations of guests.
    if sub_event_guest_registrations:
        for sub_event_guest_registration in sub_event_guest_registrations:
            sub_event_guest_registration.delete()

    # Deletes the sub-event's waiting list registrations of users.
    if sub_event_waiting_lists:
        for sub_event_waiting_list in sub_event_waiting_lists:
            sub_event_waiting_list.delete()

    # Deletes the sub-event's waiting list registrations of guests.
    if sub_event_guest_waiting_lists:
        for sub_event_guest_waiting_list in sub_event_guest_waiting_lists:
            sub_event_guest_waiting_list.delete()

    # Deletes the sub-event and its descriptions.
    sub_event_description_nb.delete()
    sub_event_description_en.delete()
    sub_event.delete()

    # Returns a JSON success response.
    return get_json(200, "Sub-event deleted!")


@login_required
def edit_event_request(request):
    """ Edits a given event. """

    if not request.POST:
        return get_json(400, 'Request must be POST.')

    data = request.POST

    # Gets the event
    event = Event.objects.get(id=int(data.get('id')))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(event, request.user):
        return get_json(400, 'You do not have the right to editing the event.')

    # Gets the new input for the event.
    name_nb = data.get('name_nb')
    name_en = data.get('name_en')
    description_nb = data.get('description_text_nb')
    description_en = data.get('description_text_en')
    email_text_nb = data.get('email_text_nb')
    email_text_en = data.get('email_text_en')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    registration_end_date = data.get('registration_end_date')
    host = data.get('host')
    attendance_cap = data.get('attendance_cap')
    price = data.get('price')

    # Sets the event's start and end date.
    event.start_date = start_date
    event.end_date = end_date

    # Sets the start and end date.
    event.start_date = start_date + '+0000'
    event.end_date = end_date + '+0000'

    # Sets the registration_end_date to None if it is not set, otherwise to the given value.
    if not registration_end_date:
        event.registration_end_date = None
    else:
        event.registration_end_date = registration_end_date + '+0000'

    # Sets the attendance_cap to None if it is not set, otherwise to the given value.4
    if not attendance_cap:
        event.attendance_cap = None

    # Sets the price to None if it is not set, otherwise to the given value.
    if not price:
        event.price = 0
    else:
        event.price = int(price)

    # Sets the event's host.
    if host == 'NTNUI':
        event.is_host_ntnui = True
    else:
        event.sports_groups = host

    # Saves the updated event.
    event.save()

    # Gets the new input for the sub-event's description.
    event_description_nb = EventDescription.objects.get(event=event, language='nb')
    event_description_en = EventDescription.objects.get(event=event, language='en')
    event_description_nb.name = name_nb
    event_description_en.name = name_en
    event_description_nb.description_text = description_nb
    event_description_en.description_text = description_en

    # Sets the email_text to None if it is not set, otherwise to the given value.
    if not email_text_nb:
        event_description_nb.custom_email_text = None
    else:
        event_description_nb.custom_email_text = email_text_nb
    if not email_text_en:
        event_description_en.custom_email_text = None
    else:
        event_description_en.custom_email_text = email_text_en

    # Saves the event's descriptions.
    event_description_nb.save()
    event_description_en.save()

    # Returns the event's ID and a JSON success response.
    return JsonResponse({'id': data.get('id'), 'message': "Edit event successful"}, status=200)


@login_required
def delete_event_request(request, event_id):
    """ Deletes a given event and all its related objects. """

    event = Event.objects.get(id=int(event_id))

    # Checks if the user has the right to alter the event.
    if not can_user_alter_event(event, request.user):
        return get_json(400, 'You do not have the right to deleting the event.')

    # Gets the event's descriptions.
    event_description_nb = EventDescription.objects.get(event=event, language='nb')
    event_description_en = EventDescription.objects.get(event=event, language='en')

    # Gets the event's user and guest registrations.
    event_registrations = EventRegistration.objects.filter(event=event)
    event_waiting_lists = EventWaitingList.objects.filter(event=event)
    event_guest_waiting_lists = EventGuestWaitingList.objects.filter(event=event)
    event_guest_registrations = EventGuestRegistration.objects.filter(event=event)

    # Checks if the event has categories.
    if Category.objects.filter(event=event).exists():
        categories = Category.objects.filter(event=event)

        # Deletes the categories.
        for category in categories:
            delete_category(category)

    # Deletes the event's registration of users.
    if event_registrations:
        for event_registration in event_registrations:
            event_registration.delete()

    # Deletes the event's registrations of guests.
    if event_guest_registrations:
        for event_guest_registration in event_guest_registrations:
            event_guest_registration.delete()

    # Deletes the event's waiting list registrations of users.
    if event_waiting_lists:
        for event_waiting_list in event_waiting_lists:
            event_waiting_list.delete()

    # Deletes the event's waiting list registration of guests.
    if event_guest_waiting_lists:
        for event_guest_waiting_list in event_guest_waiting_lists:
            event_guest_waiting_list.delete()

    # Deletes the event and its descriptions.
    event_description_nb.delete()
    event_description_en.delete()
    event.delete()

    # Returns a JSON success response.
    return get_json(200, "Event deleted!")


def can_user_alter_event(event, user):
    """ Checks if the user can create, edit and delete the event. """

    # Checks which host(s) which is hosting the event.
    hosts = set(event.get_host())

    # Checks which groups the user can create, edit and delete events for.
    groups = []
    for sports_group in get_groups_user_can_create_events_for(user):
        if type(sports_group) is dict:
            groups.append(str(sports_group['name']))
        else:
            groups.append(str(sports_group))

    # Checks if the user can alter the event.
    if hosts.intersection(set(groups)):
        return True

    # The user doesn't have rights to alter the event.
    return False
