from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils import translation
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership

from . import create_event, get_events
from events.models.event import Event, EventDescription, EventRegistration, EventWaitingList, EventGuestWaitingList, EventGuestRegistration
from events.models.sub_event import SubEvent, SubEventDescription, SubEventRegistration, SubEventWaitingList, SubEventGuestWaitingList, SubEventGuestRegistration
from events.models.category import Category, CategoryDescription
from events.models.guest import Guest
from accounts.models import User
from django.core.validators import validate_email, validate_integer
from django.core.mail import send_mail
#from events.ntnui.apps.accounts.models import User


def create_category_request(request):
    if request.POST:
        name_nb = request.POST.get("name_nb")
        name_en = request.POST.get("name_en")

        # validate
        category = Category.objects.create(event=Event.objects.get(id=int(request.POST.get("event"))))

        CategoryDescription.objects.create(category=category, name=name_nb, language='nb')
        CategoryDescription.objects.create(category=category, name=name_en, language='en')
        return JsonResponse({
            'id': category.id,
            'message': _('New category successfully created!')},
            status=201)


def create_sub_event_request(request):
    if request.POST:
        print(request.POST)
        name_nb = request.POST.get("name_nb")
        name_en = request.POST.get("name_en")
        email_text_nb = request.POST.get("email_nb")
        email_text_en = request.POST.get("email_en")

        # If price is not given a value, price is set to 0
        price = request.POST.get('price')
        if price == "":
            price = 0

        # if attendance_cap is "" its set to None
        attendance_cap = request.POST.get('attendance_cap')
        if attendance_cap == "":
            attendance_cap = None

        registration_end_date = request.POST.get('registration_end_date')
        if registration_end_date == "":
            registration_end_date = None;

        category_id =  request.POST.get("category", "")

        if category_id == "":
            event_id = int(request.POST.get("event"))
            print(Category.objects.filter(event__id=event_id, categorydescription__name='Non categorized').exists())
            if not Category.objects.filter(event__id=event_id, categorydescription__name='Non categorized').exists():
                category = Category.objects.create(event=Event.objects.get(id=event_id))
                CategoryDescription.objects.create(category=category, name="Ikke kategorisert", language='nb')
                CategoryDescription.objects.create(category=category, name="Non categorized", language='en')
            else:
                category = Category.objects.filter(event__id=event_id, categorydescription__name='Non categorized')[0]
        else:
            category = Category.objects.get(id=category_id)

        # validate
        sub_event = SubEvent.objects.create(start_date=request.POST.get("start_date"),
                                            end_date=request.POST.get("end_date"),
                                            price=price,
                                            registration_end_date=registration_end_date,
                                            attendance_cap=attendance_cap,
                                            category=category)

        SubEventDescription.objects.create(sub_event=sub_event, name=name_nb, custom_email_text =email_text_nb, language='nb')
        SubEventDescription.objects.create(sub_event=sub_event, name=name_en, custom_email_text = email_text_en, language='en')
        return JsonResponse({
            'id': sub_event.id,
            'message': _('New sub-event successfully created!')},
            status=201)


def get_main_page(request):
    """Returns the main page for events"""

    # Used to find out if the create-event button shall be rendered or not
    if request.user.is_authenticated:
        can_create_event = user_can_create_event(request.user)
    else:
        can_create_event = False

    # Get groups that are hosting events
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_main_page.html', {
        'can_create_event': can_create_event,
        'groups': groups,
    })


def get_sub_event_dic(item, request):
    # Checks if the user is signed in.
    if request.user.is_authenticated:
        attends = item.is_user_enrolled(request.user)
    else:
        # Returns false if not
        attends = False

    return {
        'start_date': item.start_date,
        'end_date': item.end_date,
        'attends': attends,
        'name': str(item),
        'price': item.price,
        'id': item.id
    }


def get_event_details(request, id):
    sub_event_list = []
    # get the event from db
    event = Event.objects.get(id=int(id))
    # check that the event got one or more categories
    if Category.objects.filter(event=event).exists():
        categories = Category.objects.filter(event=event)
        # for every category do:
        for i in range(len(categories)):
            # get all the sub-events for that category
            sub_event = SubEvent.objects.filter(category=categories[i])
            # add the category and map each sub_event to a dic
            sub_event_list.append((categories[i], list(map(lambda item: get_sub_event_dic(item, request), sub_event))))

    number_of_subevents=len(sub_event_list)

    # Checks if the user is sign in.
    if request.user.is_authenticated:
        attends = event.is_user_enrolled(request.user)
        can_create_event = user_can_create_event(request.user)
    else:
        # Returns false if not
        attends = False

    if request.user.is_authenticated:
        can_create_event = user_can_create_event(request.user)
    else:
        can_create_event = False

    if request.user.is_authenticated:
        if user_is_in_mainboard(request.user):
            is_in_mainboard = user_is_in_mainboard(request.user)
        else:
            is_in_mainboard = False

        user_boards = get_groups_user_can_create_events_for(request.user)
        event_hosts = []
        for group in event.sports_groups.all():
            event_hosts.append(group)

        is_in_board = False
        for board in user_boards:
            if board in event_hosts:
                is_in_board = True

        if is_in_mainboard or is_in_board:
            can_edit_and_delete_event = True
        else:
            can_edit_and_delete_event = False
    else:
        can_edit_and_delete_event = False

    event = {
        'name': event.name(),
        'description': event.description(),
        'start_date': event.start_date,
        'end_date': event.end_date,
        'cover_photo': event.cover_photo,
        'attends': attends,
        'id': event.id,
        'price': event.price,
        'payment_required': event.is_payment_event(),
        'host': event.get_host(),
        'place': event.place,
        'language': translation.get_language
    }

    context = {
        "event": event,
        "is_authenticated": request.user.is_authenticated,
        "sub_event_list": sub_event_list,
        'number_of_subevents': number_of_subevents,
        'can_create_event': can_create_event,
        'can_edit_and_delete_event': can_edit_and_delete_event,
        "STRIPE_KEY": settings.STRIPE_PUBLIC_KEY
    }

    return render(request, 'events/event_details.html', context)

def get_attending_events_page(request):

    # Used to find out if the create-event button shall be rendered or not
    if request.user.is_authenticated:
        can_create_event = user_can_create_event(request.user)
    else:
        can_create_event = False

    # Get groups that are hosting events
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_attending_page.html', {
        'can_create_event': can_create_event,
        'groups': groups,
    })


def delete_event(request):
    return get_main_page(request)


# Delete event
# the commented lines are to be uncommented when created events have an eventregistration by default
def get_delete_event(request, id):
    try:
        event = Event.objects.get(id=int(id))
        eventdescription_no = EventDescription.objects.get(event=event, language='nb')
        eventdescription_en = EventDescription.objects.get(event=event, language='en')
        # eventregistration = EventRegistration.objects.get(event=event)
        # if eventregistration.payment_id != '':
        #    refund_event(request)
        event.delete()
        eventdescription_no.delete()
        eventdescription_en.delete()
        # eventregistration.delete()
    except:
        return HttpResponse("Event delete failed")

    return render(request, 'events/delete_event_page.html')



#the commented lines are to be uncommented when created subevents have a subeventregistration by default
def delete_subevent(request):
    try:
        if request.method == 'POST':
            data = request.POST
            subeventid = (data['subeventid'])
            subevent = SubEvent.objects.get(id=int(subeventid))
            subeventdescription_no = SubEventDescription.objects.get(sub_event=subevent, language='nb')
            subeventdescription_en = SubEventDescription.objects.get(sub_event=subevent, language='en')
            #subeventregistration = SubEventRegistration.objects.get(subevent=subevent)
            # subeventregistration = SubEventRegistration.objects.get(subevent=subevent)
            subevent.delete()
            subeventdescription_no.delete()
            subeventdescription_en.delete()
            # subeventregistration.delete()
    except:
        return HttpResponse("Subevent delete failed")


def get_edit_event_page(request, id):
    groups = get_groups_user_can_create_events_for(request.user)
    event = Event.objects.get(id=int(id))
    eventdescription_no = EventDescription.objects.get(event=event, language='nb')
    eventdescription_en = EventDescription.objects.get(event=event, language='en')
    attendance_cap = event.attendance_cap
    price = event.price
    # convert dates to a format that can be put as value in inputtype datetimelocal html form
    event_start_date = event.start_date
    event_end_date = event.end_date
    start_date = '{:%Y-%m-%dT%H:%M}'.format(event_start_date)
    end_date = '{:%Y-%m-%dT%H:%M}'.format(event_end_date)
    registration_end_date = '{:%Y-%m-%dT%H:%M}'.format(event.registration_end_date)

    event = {
        'name_no': eventdescription_no.name,
        'name_en': eventdescription_en.name,
        'description_text_no': eventdescription_no.description_text,
        'description_text_en': eventdescription_en.description_text,
        'email_text_no': eventdescription_no.custom_email_text,
        'email_text_en': eventdescription_en.custom_email_text,

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


def edit_event(request):
        if request.method == 'POST':
            data = request.POST

            event = Event.objects.get(id=int(data['id']))

            name_no = data['name_no']
            name_en = data['name_en']
            description_no = data['description_text_no']
            description_en = data['description_text_en']
            email_text_no = data['email_text_no']
            email_text_en = data['email_text_en']
            start_date = data['start_date']
            end_date = data['end_date']
            host = data['host']
            attendance_cap = data['attendance_cap']
            price = data['price']

            event.start_date = start_date
            event.end_date = end_date
            event.attendance_cap = attendance_cap
            event.price = price

            if host == 'NTNUI':
                event.is_host_ntnui = True
            else:
                event.sports_groups = host

            event.save()
            eventdescription_no = EventDescription.objects.get(event=event, language='nb')
            eventdescription_en = EventDescription.objects.get(event=event, language='en')

            eventdescription_no.name = name_no
            eventdescription_en.name = name_en
            eventdescription_no.description_text = description_no
            eventdescription_en.description_text = description_en
            eventdescription_no.custom_email_text = email_text_no
            eventdescription_en.custom_email_text = email_text_en
            eventdescription_no.save()
            eventdescription_en.save()

            return get_json(200, "Edit successful")

            return get_json(400, "Edit failed")


def get_events_request(request):
    return get_events.get_events(request, False)

def get_attending_events_request(request):

    return get_events.get_events(request, True)


def get_event_attendees_page(request, id, numberofsubevents):

    event = Event.objects.get(id=int(id))
    eventname = event.name()

    if int(numberofsubevents)== 0:
        subeventsexist=False
        eventregistrations = EventRegistration.objects.filter(event=event)

        attendees = []
        for registration in eventregistrations:
            user = registration.attendee
            attendees.append(user.get_full_name())

        attendees.sort()

        context = {
            'subeventsexist': subeventsexist,
            'eventname': eventname,
            'attendees_list': attendees,
        }

    else:
        subeventsexist=True
        eventcategories=Category.objects.filter(event=event)

        subeventslist=[]
        for category in eventcategories:
            subevents=SubEvent.objects.filter(category=category)
            for subevent in subevents:
                subeventslist.append(subevent)

        subevents_attendees_and_names_list=[]

        for subevent in subeventslist:
            attendees=[]
            users=[]
            subeventregistrations = SubEventRegistration.objects.filter(sub_event=subevent)
            for registration in subeventregistrations:
                user = registration.attendee
                if user not in users:
                    users.append(user)
                    user_full_name = user.get_full_name()
                    attendees.append(user_full_name)

            subevents_attendees_and_names_list.append((attendees, subevent.name()))

        context = {
                'subeventsexist': subeventsexist,
                'eventname': eventname,
                'subevents_attendees_and_name_list': subevents_attendees_and_names_list,
            }


    return render(request, 'events/event_attendees_page.html', context)


@login_required
def edit_event_request(request):
    return edit_event(request)


@login_required
def create_event_request(request):
    """Creates a new event with the given data"""
    return create_event.create_event(request)


@login_required
def get_create_event_page(request):
    """Returns the page where events are created"""

    # Checks if a user can create an event
    groups = get_groups_user_can_create_events_for(request.user)

    return render(request, 'events/create_new_event.html', {'groups': groups})


def user_can_create_event(user):
    """Checks to see if a user can create event of any kind"""

    # User is in MainBoard
    if user_is_in_mainboard(user):
        return True

    # Checks if the user is in any active board
    for board in (Board.objects.filter(Q(president=user) | Q(vice_president=user) | Q(cashier=user))):
        # Checks that the board is active
        if SportsGroup.objects.filter(active_board=board).exists():
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
    """Checks if a given user is in mainboard"""
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


def get_event(request, id):
    if Event.objects.filter(id=int(id)).exists():
        event = Event.objects.get(id=int(id))
        return JsonResponse({
            'id': event.id,
            'name': event.name(),
            'place': event.place,
            'description': event.description(),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'priority': event.priority,
            'price': event.price,
            'host': event.get_host(),
            'cover_photo': str(event.cover_photo)
        })
    return get_json(404, "Event with id: " + id + " does not exist.")


def get_json(code, message):
    """Returns JSON with the given format."""

    return JsonResponse({
        'message': message},
        status=code)


def event_send_mail(event, user):
    subject = event.name() + " - " + " - ".join(str(item) for item in event.get_host())
    from_email = 'noreply@mg.ntnui.no'
    to_email = [user.email]

    content = {'user': user,
               'event': event
               }

    msg_plain = render_to_string('events/email/event.txt', content)
    msg_html = render_to_string('events/email/event.html', content)

    send_mail(
        subject,
        msg_plain,
        from_email,
        to_email,
        html_message=msg_html,
    )


@login_required
def user_attend_event(request, event_id):
    """User: Sign-up for a free event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Gets the event, the user, and if the user can attend the event.
    user = request.user
    event = get_event_by_id(event_id)
    can_attend, error_message = user_can_attend_event(event, user)

    # Checks if the user can attend the event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif event.is_attendance_cap_exceeded():
        return get_json(400, 'The event is full.')
    else:
        return attend_event(event, user, None)


@login_required
def user_attend_payment_event(request, event_id):
    """User: Sign-up for a payment event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Gets the event, the user, and if the user can attend the event.
    user = request.user
    event = get_event_by_id(event_id)
    can_attend, error_message = user_can_attend_event(event, user)

    # Checks if the user can attend the event.
    # Creates the payment for the event registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif event.is_attendance_cap_exceeded():
        return get_json(400, 'The event is full.')
    else:
        accepted, charge, error_message = payment_accepted(request, event, user)

    # Checks if the payment went through.
    # Creates the event registration if the payment were accepted.
    if not accepted:
        return error_message
    else:
        return attend_event(event, user, charge.id)


@login_required
def user_waiting_list_event(request, event_id):
    """User: Sign-up for the event's waiting list."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    # Gets the event, the user, and if the user can attend the event.
    user = request.user
    event = get_event_by_id(event_id)
    can_attend, error_message = user_can_attend_event(event, user)

    # Checks if the user can join the event's waiting list.
    # Creates the waiting list registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif not event.is_attendance_cap_exceeded():
        return get_json(400, 'The event still has open spots.')
    else:
        return waiting_list_event(event, user, None)


def guest_attend_event(request, event_id):
    """Guest: Sign-up for a free event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)
    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the guest, and if the guest can attend the event.
    event = get_event_by_id(event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_event(event, guest)

    # Checks if the user can attend the event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The event is full.')
    else:
        return attend_event(event, guest, None)


def guest_attend_payment_event(request, event_id):
    """Guest: Sign-up for a payment event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')
    print(request.POST.get('email'))
    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)

    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the guest, and if the user can attend the event.
    event = get_event_by_id(event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_event(event, guest)

    # Checks if the user can attend the event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The event is full.')
    else:
        accepted, charge, error_message = payment_accepted(request, event, guest)

    # Checks if the payment went through.
    # Creates the event registration if the payment were accepted.
    if not accepted:
        if created:
            guest.delete()
        return error_message
    else:
        return attend_event(event, guest, charge.id)


def guest_waiting_list_event(request, event_id):
    """Guest: Sign-up for the event's waiting list."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)
    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the g, and if the user can attend the event.
    event = get_event_by_id(event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_event(event, guest)

    # Checks if the user can attend the event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif not event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The event still has open spots.')
    else:
        return attend_event(event, guest, None)


def attend_event(event, attendee, payment_id):
    """User or Guest: Create event registration."""

    # Creates event registration for either a user or a guest, depending on the class of 'attendee'.
    if isinstance(attendee, User):
        event.user_attend_event(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        event.guest_attend_event(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Only users and guests can attend.")

    # Sends confirmation email after signing-up for the event.
    event_send_mail(event, attendee)
    return get_json(201, 'Signed-up for the event!')


def waiting_list_event(event, attendee, payment_id):
    """User or Guest: Create waiting list registration."""

    # Creates event waiting list registration for either a user or a guest, depending on the class of 'attendee'.
    if isinstance(attendee, User):
        event.user_attend_waiting_list(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        event.guest_attend_waiting_list(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Attendee is neither user nor guest.")

    # Sends confirmation mail after successfully signing-up for the event.
    # event_send_mail(event, attendee)
    return get_json(201, 'Signed-up for the waiting list!')


def user_can_attend_event(event, user):
    """User: JSON-response if the user can't attend the event."""

    # Checks if the user already attends the event.
    if event.is_user_enrolled(user):
        return False, get_json(400, 'The user already attends the event.')
    # Checks if the user is on the event's waiting list.
    elif event.is_user_on_waiting_list(user):
        return False, get_json(400, 'The user is on the waiting list.')
    # Checks if the event's registration has ended.
    elif event.is_registration_ended():
        return False, get_json(400, 'The event registration has ended.')
    # The user can attend the event.
    else:
        return True, None


def guest_can_attend_event(event, guest):
    """Guest: JSON-response if the guest can't attend the event."""

    # Checks if the guest already attends the event.
    if event.is_guest_enrolled(guest):
        return False, get_json(400, 'The guest already attends the event.')
    # Checks if the guest is on the event's waiting list.
    elif event.is_guest_on_waiting_list(guest):
        return False, get_json(400, 'The guest is on the waiting list.')
    # Checks if the event's registration has ended.
    elif event.is_registration_ended():
        return False, get_json(400, 'The event registration has ended.')
    # The user can attend the event.
    else:
        return True, None


def payment_accepted(request, event, attendee):
    """User or Guest: Create payment with Stripe."""

    # Gets the necessary information to create the payment.
    amount = event.price * 100
    description = str(event.name()) + " - " + str(attendee)
    email = request.POST.get('stripEmail')
    token = request.POST.get('stripeToken')
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Charges the attendee's card.

    charge = stripe.Charge.create(receipt_email=email, source=token, amount=amount,
                                    currency="NOK", description=description)

    # Payment accepted.
    return True, charge, None


def validate_guest_data(data):
    """Guest: Validate the input data when registering as guest for an event."""

    try:
        Event.objects.get(id=data.get('id'))
        validate_email(data.get('email'))
        validate_integer(data.get('phone'))
    except ValidationError as e:
        return e.message
    except Event.DoesNotExist:
        return _("Event dose not exist")
    return None


def get_or_create_guest(email, first_name, last_name, phone):
    """Guest: Get an existing guest or create a new one."""

    guest, created = Guest.objects.get_or_create(email=email, first_name=first_name, last_name=last_name, phone_number=phone)
    return guest, created


def get_event_by_id(event_id):
    """Gets the event which the event_id is associated with."""

    return Event.objects.get(id=event_id)


@login_required
def user_unattend_event(request):
    """User: Sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    event_id = request.POST.get('id')

    # Sign off event.
    return unattend_event(event_id, request.user)


@login_required
def user_unattend_payment_event(request):

    return get_json(404, "Contact the host for refunding.")

    """
    if request.POST:
        try:
            id = request.POST.get('id')
            event = Event.objects.get(id=int(id))
            stripe.api_key = settings.STRIPE_SECRET_KEY

            event_registration = EventRegistration.objects.get(attendee=request.user, event=event)

            # refund user
            refund = stripe.Refund.create(
                charge=event_registration.payment_id
            )
            if refund:
                remove_attendance(event.id, request.user)
                return get_json(200, 'Refund accepted')
        except:
            return get_json(404, 'Woops, something went wrong')
    return get_json(404, 'Request must be post!')
    """


@login_required
def user_unattend_waiting_list_event(request):
    """User sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    user = request.user
    event_id = request.POST.get('id')

    # Sign off event.
    return sign_off_waiting_list(int(event_id), user)


def unattend_event(event_id, attendee):
    """User sign-off for event"""

    # Gets event.
    event = get_event_by_id(event_id)

    # Checks that the user is signed up for the event.
    if not event.is_user_enrolled(attendee):
        return get_json(400, 'You not signed up the event.')
    # Sign-off the event.
    try:
        EventRegistration.objects.get(event=event, attendee=attendee).delete()

        if len(event.get_waiting_list()) > 0 and not event.is_payment_event():

            attendee, payment_id = event.waiting_list_next()

            if isinstance(attendee, User):
                EventWaitingList.objects.filter(event=event, attendee=attendee).delete()
            else:
                EventGuestWaitingList.objects.filter(event=event, attendee=attendee).delete()

            attend_event(event_id, attendee, payment_id)
        return get_json(201, 'Signed-off the event!')
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the event.")


def sign_off_waiting_list(event_id, attendee):
    """User sign-off the event's waiting list."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user is signed up for the event.
    if event.is_user_enrolled(attendee):
        return get_json(400, 'You are already signed off the event.')
    # Sign-off the event.
    try:
        EventWaitingList.objects.get(event=event, attendee=attendee).delete()

        return get_json(201, 'Signed-off the waiting list!')
    # Couldn't sign-off the event.
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the waiting list.")


@login_required
def user_attend_sub_event(request, sub_event_id):
    """User: Sign-up for a free sub-event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Gets the event, the user, and if the user can attend the event.
    user = request.user
    sub_event = get_sub_event_by_id(sub_event_id)
    can_attend, error_message = user_can_attend_sub_event(sub_event, user)

    # Checks if the user can attend the sub-event.
    # Creates the sub-event registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif sub_event.is_attendance_cap_exceeded():
        return get_json(400, 'The sub-event is full.')
    else:
        return attend_sub_event(sub_event, user, None)


@login_required
def user_attend_payment_sub_event(request, sub_event_id):
    """User: Sign-up for a payment sub-event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Gets the sub-event, the user, and if the user can attend the sub-event.
    user = request.user
    sub_event = get_sub_event_by_id(sub_event_id)
    can_attend, error_message = user_can_attend_sub_event(sub_event, user)

    # Checks if the user can attend the event.
    # Creates the payment for the event registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif sub_event.is_attendance_cap_exceeded():
        return get_json(400, 'The sub-event is full.')
    else:
        accepted, charge, error_message = payment_accepted(request, sub_event, user)

    # Checks if the payment went through.
    # Creates the sub-event registration if the payment were accepted.
    if not accepted:
        return error_message
    else:
        return attend_sub_event(sub_event, user, charge.id)


@login_required
def user_waiting_list_sub_event(request, sub_event_id):
    """User: Sign-up for the sub-event's waiting list."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    # Gets the event, the user, and if the user can attend the event.
    user = request.user
    sub_event = get_sub_event_by_id(sub_event_id)
    can_attend, error_message = user_can_attend_sub_event(sub_event, user)

    # Checks if the user can join the sub-event's waiting list.
    # Creates the waiting list registration if the user is eligible to attend.
    if not can_attend:
        return error_message
    elif not sub_event.is_attendance_cap_exceeded():
        return get_json(400, 'The sub-event still has open spots.')
    else:
        return waiting_list_sub_event(sub_event, user, None)


def guest_attend_sub_event(request, sub_event_id):
    """Guest: Sign-up for a free sub-event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)
    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the guest, and if the guest can attend the event.
    sub_event = get_sub_event_by_id(sub_event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_sub_event(sub_event, guest)

    # Checks if the user can attend the event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif sub_event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The sub-event is full.')
    else:
        return attend_sub_event(sub_event, guest, None)


def guest_attend_payment_sub_event(request, sub_event_id):
    """Guest: Sign-up for a payment sub-event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)
    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the guest, and if the user can attend the event.
    sub_event = get_sub_event_by_id(sub_event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_sub_event(sub_event, guest)

    # Checks if the user can attend the sub-event.
    # Creates the payment if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif sub_event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The event is full.')
    else:
        charge = payment_accepted(request, sub_event, guest)

    # Checks if the payment went through.
    # Creates the event registration if the payment were accepted.
    if not charge[0]:
        if created:
            guest.delete()
        return charge[1]
    else:
        return attend_sub_event(sub_event, guest, charge.id)


def guest_waiting_list_sub_event(request, sub_event_id):
    """Guest: Sign-up for the sub-event's waiting list."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be POST.')

    # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
    failure_message = validate_guest_data(request.POST)
    if failure_message:
        return get_json(404, failure_message)

    # Gets the validated data from POST request.
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    phone = request.POST.get('phone')

    # Gets the event, the g, and if the user can attend the event.
    sub_event = get_sub_event_by_id(sub_event_id)
    guest, created = get_or_create_guest(email, first_name, last_name, phone)
    can_attend, error_message = guest_can_attend_sub_event(sub_event, guest)

    # Checks if the user can attend the sub-event.
    # Creates the event registration if the user is eligible to attend.
    if not can_attend:
        if created:
            guest.delete()
        return error_message
    elif not sub_event.is_attendance_cap_exceeded():
        if created:
            guest.delete()
        return get_json(400, 'The sub-event still has open spots.')
    else:
        return attend_sub_event(sub_event, guest, None)


def attend_sub_event(sub_event, attendee, payment_id):
    """User or Guest: Create sub-event registration."""

    # Creates sub-event registration for either a user or a guest, depending on the class of 'attendee'.
    if isinstance(attendee, User):
        sub_event.user_attend_sub_event(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        sub_event.guest_attend_sub_event(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Only users and guests can attend.")

    # Sends confirmation email after signing-up for the sub-event.
    # event_send_mail(sub_event, attendee)
    return get_json(201, 'Signed-up for the event!')


def waiting_list_sub_event(sub_event, attendee, payment_id):
    """User or Guest: Create waiting list registration."""

    # Creates sub-event waiting list registration for either a user or a guest, depending on the class of 'attendee'.
    if isinstance(attendee, User):
        sub_event.user_attend_waiting_list(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        sub_event.guest_attend_waiting_list(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Attendee is neither user nor guest.")

    # Sends confirmation mail after successfully signing-up for the sub-event.
    # event_send_mail(event, attendee)
    return get_json(201, 'Signed-up for the waiting list!')


def user_can_attend_sub_event(sub_event, user):
    """User: JSON-response if the user can't attend the sub-event."""

    # Checks if the user already attends the event.
    if sub_event.is_user_enrolled(user):
        return False, get_json(400, 'The user already attends the event.')
    # Checks if the user is on the event's waiting list.
    elif sub_event.is_user_on_waiting_list(user):
        return False, get_json(400, 'The user is on the waiting list.')
    # Checks if the event's registration has ended.
    elif sub_event.is_registration_ended():
        return False, get_json(400, 'The event registration has ended.')
    # The user can attend the event.
    else:
        return True, None


def guest_can_attend_sub_event(sub_event, guest):
    """Guest: JSON-response if the guest can't attend the sub-event."""

    # Checks if the guest already attends the sub-event.
    if sub_event.is_guest_enrolled(guest):
        return False, get_json(400, 'The guest already attends the sub-event.')
    # Checks if the guest is on the sub-event's waiting list.
    elif sub_event.is_guest_on_waiting_list(guest):
        return False, get_json(400, 'The guest is on the waiting list.')
    # Checks if the sub-event's registration has ended.
    elif sub_event.is_registration_ended():
        return False, get_json(400, 'The sub-event registration has ended.')
    # The user can attend the sub-event.
    else:
        return True, None


def get_sub_event_by_id(sub_event_id):
    """Gets the event which the event_id is associated with."""

    return SubEvent.objects.get(id=sub_event_id)


@login_required
def user_unattend_sub_event(request):
    """User: Sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    sub_event_id = request.POST.get("id")

    # Sign off event.
    return unattend_sub_event(sub_event_id, request.user)


@login_required
def user_unattend_payment_sub_event(request):

    return get_json(404, "Contact the host for refunding.")

    """
    if request.POST:
        try:
            id = request.POST.get('id')
            event = Event.objects.get(id=int(id))
            stripe.api_key = settings.STRIPE_SECRET_KEY

            event_registration = EventRegistration.objects.get(attendee=request.user, event=event)

            # refund user
            refund = stripe.Refund.create(
                charge=event_registration.payment_id
            )
            if refund:
                remove_attendance(event.id, request.user)
                return get_json(200, 'Refund accepted')
        except:
            return get_json(404, 'Woops, something went wrong')
    return get_json(404, 'Request must be post!')
    """


@login_required
def user_unattend_waiting_list_sub_event(request):
    """User sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    user = request.user
    event_id = request.POST.get('id')

    # Sign off event.
    return sign_off_waiting_list(int(event_id), user)


def unattend_sub_event(sub_event_id, attendee):
    """User sign-off for event"""

    # Gets event.
    sub_event = get_sub_event_by_id(sub_event_id)

    # Checks that the user is signed up for the event.
    if not sub_event.is_user_enrolled(attendee):
        return get_json(400, 'You not signed up the event.')
    # Sign-off the event.
    try:
        SubEventRegistration.objects.get(sub_event=sub_event, attendee=attendee).delete()

        if len(sub_event.get_waiting_list()) > 0 and not sub_event.is_payment_event():

            attendee, payment_id = sub_event.waiting_list_next()

            if isinstance(attendee, User):
                SubEventWaitingList.objects.filter(sub_event=sub_event, attendee=attendee).delete()
            else:
                SubEventGuestWaitingList.objects.filter(sub_event=sub_event, attendee=attendee).delete()

            attend_sub_event(sub_event_id, attendee, payment_id)

        return get_json(201, 'Signed-off the event!')
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the event.")


def sign_off_waiting_list(sub_event_id, attendee):
    """User sign-off the event's waiting list."""

    # Get event.
    sub_event = SubEvent.objects.get(id=sub_event_id)

    # Checks that the user is signed up for the event.
    if sub_event.is_user_enrolled(attendee):
        return get_json(400, 'You are already signed off the event.')
    # Sign-off the event.
    try:
        SubEventWaitingList.objects.get(sub_event=sub_event, attendee=attendee).delete()

        return get_json(201, 'Signed-off the waiting list!')
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the waiting list.")
