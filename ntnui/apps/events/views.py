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
from events.models.sub_event import SubEvent, SubEventRegistration
from events.models.category import Category
from events.models.guest import Guest
from accounts.models import User
from django.core.validators import validate_email, validate_integer
from django.core.mail import send_mail


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
        attends = item.attends(request.user)
    else:
        # Returns false if not
        attends = False

    return {
        'start_date': item.start_date,
        'end_date': item.end_date,
        'attends': attends,
        'name': str(item),
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


    # Checks if the user is sign in.
    if request.user.is_authenticated:
        attends = event.user_attends(request.user)
        can_create_event = user_can_create_event(request.user)
    else:
        # Returns false if not
        attends = False
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
        #'require_payment': event.payment_required(),
        'host': event.get_host(),
        'place': event.place,
        'language': translation.get_language
    }

    context = {
        "event": event,
        "is_authenticated": request.user.is_authenticated,
        "sub_event_list": sub_event_list,
        'can_create_event': can_create_event,
        'can_edit_and_delete_event': can_edit_and_delete_event,
        "STRIPE_KEY": settings.STRIPE_PUBLIC_KEY
    }

    return render(request, 'events/event_details.html', context)


def delete_event(request):

    return get_main_page(request)


def get_delete_event(request, id):
    try:
        event = Event.objects.get(id=int(id))
        eventdescription_no = EventDescription.objects.get(event=event, language='nb')
        eventdescription_en = EventDescription.objects.get(event=event, language='en')
        event.delete()
        eventdescription_no.delete()
        eventdescription_en.delete()
    except:
        return HttpResponse("Delete failed")

    return render(request, 'events/delete_event_page.html')


def get_edit_event_page(request, id):

    groups = get_groups_user_can_create_events_for(request.user)
    event = Event.objects.get(id=int(id))
    eventdescription_no = EventDescription.objects.get(event=event, language='nb')
    eventdescription_en = EventDescription.objects.get(event=event, language='en')
    #convert dates to a format that can be put as value in inputtype datetimelocal html form
    event_start_date = event.start_date
    event_end_date = event.end_date
    start_date='{:%Y-%m-%dT%H:%M}'.format(event_start_date)
    end_date='{:%Y-%m-%dT%H:%M}'.format(event_end_date)
    event = {
        'name_no': eventdescription_no.name,
        'name_en': eventdescription_en.name,
        'description_no': eventdescription_no.description_text,
        'description_en': eventdescription_en.description_text,
        'email_text_no': eventdescription_no.custom_email_text,
        'email_text_en': eventdescription_en.custom_email_text,

        'start_date': start_date,
        'end_date': end_date,
        'id': event.id,
        'host': event.get_host(),
        'place': event.place,
        'groups': groups
    }

    context = {
        "event": event,
    }
    return render(request, 'events/edit_event_page.html', context)

def edit_event(request):
    try:
        if request.method == 'POST':
            data = request.POST

            event = Event.objects.get(id=int(data['event_id']))

            name_no=data['name_no']
            name_en=data['name_en']
            description_no=data['description_text_no']
            description_en = data['description_text_en']
            email_text_no=data['email_text_no']
            email_text_en=data['email_text_en']
            start_date=data['start_date']
            end_date = data['end_date']
            host = data['host']

            event.start_date = start_date
            event.end_date = end_date
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

            return HttpResponse("Edit successful")
    except:
        return HttpResponse("Edit failed")


def get_events_request(request):
    return get_events.get_events(request)

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


def get_json(code, message):
    """Returnes json with the given format"""
    return JsonResponse({
        'message': message},
        status=code)



























@login_required
def add_attendance_to_event(request):
    """Event sign-up for users with request"""

    # Checks that the request is POST.
    if request.POST:
        # Gets the required variable.
        event_id = request.POST.get('id')
        # User sign-up for event.
        return attend_event(int(event_id), request.user, None)
    # Failure JSON message, the request isn't POST.
    return get_json(400, 'Request must be post')


def refund_event(request):
    """Refunds the payment for the event"""

    # Checks that the request is POST.
    if request.POST:
        try:
            event_id = request.POST.get('id')
            event = Event.objects.get(id=int(event_id))
            stripe.api_key = settings.STRIPE_SECRET_KEY

            event_registration = EventRegistration.objects.get(attendee=request.user, event=event)

            # refund user
            refund = stripe.Refund.create(
                charge=event_registration.payment_id
            )
            if refund:
                sign_off_event(event.id, request.user)
                return get_json(200, 'Refund accepted')
        except:
            return get_json(404, 'Woops, something went wrong')
    return get_json(404, 'Request must be post!')

@login_required
def remove_attendance_from_event(request):
    """User: sign off the event (main)."""

    # Check that the request is POST.
    if request.POST:
        # Get variables to retrieve the user and event.
        user = request.user
        event_id = int(request.POST.get('id'))
        # Sign off event.
        return sign_off_event(event_id, user)
    # Failure JSON message, the request isn't POST.
    return get_json(400, 'Request is not POST.')
























def waiting_list_event(event_id, user, payment_id):

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user isn't already signed up for the event.
    if not event.user_attends(user=user):
        # Checks that the user isn't already on the event's waiting list.
        if event.user_on_waiting_list(user=user):
            # Checks if the event has an end date for registration, and that it ain't passed.
            if event.check_sign_up_end_date():
                # Checks that the event is capped out.
                if not event.check_attendance_cap():

                    # Free event.
                    if not event.payment_required():
                        try:
                            # Try to sign up for the event, without payment.
                            event.attend_waiting_list(attendee=user, registration_time=datetime.now())
                        except:
                            # Failure JSON message, couldn't sign up for the event.
                            return get_json(400, "Couldn't sign up for event.")

                    # Priced event.
                    else:
                        try:
                            # Try to sign up for the event, without payment.
                            event.attend_waiting_list(attendee=user, payment_id=payment_id, registration_time=datetime.now())
                        except:
                            # Failure JSON message, couldn't sign up for the event.
                            return get_json(400, "Couldn't sign up for event.")

                    # Success JSON message.
                    return get_json(201, 'You are now signed up for the waiting list.')
                # Failure JSON message, the event is capped out.
                return get_json(400, 'The event is not capped out.')
            # Failure JSON message, the user is already signed up for the event.
            return get_json(400, 'The event registration has ended.')
        # Failure JSON message, the user is already on the event's waiting list.
        return get_json(400, 'Already signed up for the waiting list.')
    # Failure JSON message, the user is already signed up for the event.
    return get_json(400, 'Already signed up for this event.')



"""
    if isinstance(attendee, User):
        # Checks that the user isn't already signed up for the event.
        if event.user_attends(attendee):
            return get_json(400, 'Error: already signed up for the event.')
        # Checks that the user isn't already the event's waiting list.
        if event.user_on_waiting_list(attendee):
            return get_json(400, 'Error: already on the waiting list.')
"""









def create_guest(event_id, email, first_name, last_name, phone):

    # Get event.
    event = Event.objects.get(id=event_id)

    guest_exists = EventGuestRegistration.objects.filter(event=event, attendee__email=email, attendee__first_name=first_name, attendee__last_name=last_name, attendee__phone_number=phone).exists()

    if not guest_exists:
        return Guest.objects.create(email=email, first_name=first_name, last_name=last_name, phone_number=phone)
    else:
        return None




def add_attendance_to_event_guest(request):
    """Adds attendance to the given event for the given guest"""
    if request.POST:
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return get_json(404, failure_message)

        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        event_id = request.POST.get('id')

        guest = create_guest(event_id, email, first_name, last_name, phone)
        if guest is not None:
            return attend_event(event_id, guest, None)
        else:
            return get_json(400, 'Requeeeewfqwrfwregewrgfegqwgrgwrqgst must be post')

    return get_json(400, 'Request must be post')


def validate_guest_data(data):
    try:
        Event.objects.get(id=data.get('id'))
        validate_email(data.get('email'))
        validate_integer(data.get('phone'))
    except ValidationError as e:
        return e.message
    except Event.DoesNotExist:
        return _("Event dose not exist")
    return None









def attend_event(event_id, attendee, payment_id):

    # Get event.
    event = Event.objects.get(id=event_id)

    # Check whether the event has an end date for registration, and if so, if it's exceeded.
    if not event.check_sign_up_end_date():
        return get_json(400, 'The event registration has ended.')
    # Checks whether the event has an attendance cap, and if so, if it's reached.
    if not event.check_attendance_cap():
        return get_json(400, 'The event has reached its attendance cap.')

    try:
        # Sign-up for event as user.
        if isinstance(attendee, User):
            event.user_attend_event(attendee, payment_id, datetime.now())
        # Sign-up for event as guest.
        elif isinstance(attendee, Guest):
            event.guest_attend_event(attendee, payment_id, datetime.now())
        # Illegal argument, attendee is neither user nor guest.
        else:
            return get_json(400, "Attendee is neither user nor guest.")
    except:
        # Couldn't sign up for the event.
        return get_json(400, "Could not sign up for the event.")

    # Sends confirmation mail after successfully signing-up for the event.
    event_send_mail(event, attendee)
    return get_json(201, 'Signed-up for the event!')


def waiting_list_event(event_id, guest, payment_id):

    # Get event
    event = Event.objects.get(id=event_id)

    # Check whether the event has an end date for registration, and if so, if it's exceeded.
    if not event.check_sign_up_end_date():
        return get_json(400, 'Error: the event registration has ended.')
    # Checks whether the event has an attendance cap, and if so, if it's reached.
    if not event.check_attendance_cap():
        return get_json(400, 'Error: the event has reached its attendance cap.')



        return get_json(400, 'Already signed up for the waiting list.')
    # Checks if the event has an end date for registration, and that it ain't passed.
    elif event.check_sign_up_end_date():
        return get_json(400, 'The event registration has ended.')
    # Checks that the event is capped out.
    elif not event.check_attendance_cap():
        return get_json(400, 'The event is not capped out.')

    # Free event.
    elif not event.payment_required():
        try:
            # Try to sign up for the event, without payment.
            event.guest_attend_waiting_list(attendee=guest, registration_time=datetime.now())
            return get_json(201, 'You are now signed up for the waiting list.')
        except:
            return get_json(400, "Couldn't sign up for event.")

    # Priced event.
    else:
        try:
            # Try to sign up for the event, with payment.
            event.guest_attend_waiting_list(attendee=guest, payment_id=payment_id, registration_time=datetime.now())
            return get_json(201, 'You are now signed up for the waiting list.')
        except:
            # Failure JSON message, couldn't sign up for the event.
            return get_json(400, "Couldn't sign up for event.")


"""

# Checks that the guest isn't signed up for the event
    if event.guest_attends(guest=guest):
        return get_json(400, 'Already signed up for this event.')
    # Checks that the guest isn't on the event's waiting list
    elif event.user_on_waiting_list(guest=guest):

"""



"""
def sign_off_event(event_id, user):

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user is signed up for the event.
    if event.user_attends(user=user):

        try:
            # Try to sign off the event.
            EventRegistration.objects.get(event=event, attendee=user).delete()

            if event.waiting_list_count() > 0:

                if event.next_on_waiting_list() is not None:

                    user_or_guest, attendee, payment_id = event.next_on_waiting_list()

                    if user_or_guest == 'user':
                        attend_event(event_id, attendee, payment_id)
                        EventWaitingList.objects.filter(event=event, attendee=attendee).delete()
                    else:
                        guest_attend_event(event_id, attendee, payment_id)
                        EventGuestWaitingList.objects.filter(event=event, attendee=attendee).delete()

            # Transfers the next person on the waiting list
            event.next_on_waiting_list()
            return get_json(201, 'You are now signed off the event.')
        except:
            # Failure JSON message, couldn't sign off the event.
            return get_json(400, "Couldn't sign off the event.")

    return get_json(400, 'You are already signed off the event.')

"""






@login_required
def sign_off_waiting_list_event(request):
    """User: sign off the event's waiting list (main)."""

    # Check that the request is POST.
    if request.POST:
        # Get variables to retrieve the user and event.
        user = request.user
        event_id = int(request.POST.get('id'))
        # Sign off event.
        return sign_off_waiting_list(event_id, user)
    # Failure JSON message, the request isn't POST.
    return get_json(400, 'Request is not POST.')


def sign_off_waiting_list(event_id, user):
    """"User: sign off the event's waiting list."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user on the event's waiting list.
    if event.user_on_waiting_list(user=user):
        try:
            # Try to sign off the waiting list.
            EventWaitingList.objects.get(event=event, attendee=user).delete()


            #if event.check_attendance_cap() and EventWaitingList.objects.filter(event=event) > 0:

            return get_json(201, 'You are now signed off the event.')


        except:
            # Failure JSON message, couldn't sign off the waiting list.
            return get_json(400, "Couldn't sign off the event.")
    return get_json(400, 'You are already signed off the event.')

















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
def add_attendance_from_subevent(request):
    """Add a user to the given sub-event"""
    if request.POST:
        id = request.POST.get('id')
        sub_event = SubEvent.objects.get(id=int(id))
        if sub_event.registration_end_date is None or sub_event.registration_end_dateevent.registration_end_date.replace(
                tzinfo=None) > datetime.now():
            if sub_event.attendance_cap is None or sub_event.attendance_cap > SubEventRegistration.objects.filter(
                    sub_event=sub_event).count():
                # Checks that the user is not already attending
                if not SubEventRegistration.objects.filter(sub_event=sub_event, attendee=request.user).exists():
                    try:
                        SubEventRegistration.objects.create(sub_event=sub_event, attendee=request.user,
                                                            registration_time=datetime.now())
                        return get_json(201, 'Success')
                    except:
                        return get_json(400, 'Could not join event')
                    return get_json(400, 'You are already attending this event')
                return get_json(400, 'Event has reached its maximum number of participants')
        return get_json(400, 'The registration period has ended')
    return get_json(400, 'request is not post')


@login_required
def remove_attendance_from_subevent(request):
    """Removes the given user from the given sub-event"""
    if request.POST:
        try:
            id = request.POST.get('id')
            if SubEventRegistration.objects.filter(sub_event__id=int(id), attendee=request.user).exists():
                registration = SubEventRegistration.objects.get(sub_event__id=int(id), attendee=request.user)
                registration.delete()
                return get_json(201, 'Success')
            return get_json(400, 'Attendance dose not exists')
        except:
            return get_json(400, 'Could not remove attendence')
    return get_json(400, 'request is not post')


def payment_for_event(request, id):
    if request.POST:
        try:
            event = Event.objects.get(id=int(id))
            token = request.POST.get('stripeToken')
            email = request.POST.get('stripEmail')
            stripe.api_key = settings.STRIPE_SECRET_KEY
            amount = event.price * 100
            name = request.user
            description = str(event.name()) + " - " + str(name)
            # Charge the user's card:
            charge = stripe.Charge.create(
                amount=amount,
                currency="NOK",
                description=description,
                source=token,
                receipt_email=email
            )
            if charge:
                attend_event(int(id), request.user, charge.id)
                return get_json(201, 'Signed-up for the event!')
        except:
            return get_json(404, 'Payment not excepted')
    return get_json(404, 'Request must be post.')





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
    return get_json(404, "Event with id: " + id + " dose not exist")


