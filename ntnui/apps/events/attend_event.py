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


def attend_event_user(request):
    """User sign-up for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    # Gets the required variable.
    event_id = request.POST.get('id')
    if not request.POST:
        return get_json(400, 'Request must be post')

    # User sign-up for the event's waiting list.
    return attend_event(int(event_id), request.user, None)


@login_required
def sign_off_event_user(request):
    """User sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    user = request.user
    event_id = request.POST.get('id')

    # Sign off event.
    return sign_off_event(int(event_id), user)


def attend_payment_event_user(request):
    """User sign-up for a payment event"""

    # Checks that the request is POST.
    if request.POST:

        # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return get_json(404, failure_message)

        # Get validated data from POST request.
        event_id = request.POST.get('id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        try:
            event = Event.objects.get(id=int(event_id))
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
                guest = create_guest(event_id, email, first_name, last_name, phone)
                if isinstance(guest, Guest):
                    return attend_event(event_id, guest, charge.id)
                return get_json(201, 'Signed-up for the event!')
        except:
            return get_json(404, 'Payment not excepted')

    return get_json(404, 'Request must be POST.')


@login_required
def sign_off_payment_event_user(request):
    """User sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    user = request.user
    event_id = request.POST.get('id')

    # Sign off event.
    return sign_off_event(int(event_id), user)


def waiting_list_event_user(request):
    """Guest sign-up for the event's waiting list."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    # Gets the required variable.
    event_id = request.POST.get('id')

    # User sign-up for the event's waiting list.
    return waiting_list_event(int(event_id), request.user, None)


@login_required
def sign_off_waiting_list_event_user(request):
    """User sign-off for an event."""

    # Checks that the request is POST.
    if not request.POST:
        return get_json(400, 'Request must be post')

    user = request.user
    event_id = request.POST.get('id')

    # Sign off event.
    return sign_off_waiting_list(int(event_id), user)


def attend_event_guest(request):
    """Guest sign-up for an event."""

    # Checks that the request is POST.
    if request.POST:

        # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return get_json(404, failure_message)

        # Get validated data from POST request.
        event_id = request.POST.get('id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        # Sign-up to event as guest.
        try:
            guest = create_guest(event_id, email, first_name, last_name, phone)
            if isinstance(guest, Guest):
                return attend_event(event_id, guest, None)
        # Couldn't sign up for the event.
        except:
            return get_json(400, "Could not sign up for the event.")

    return get_json(400, 'Request must be POST.')


def attend_payment_event_guest(request):
    """Guest sign-up for a payment event."""

    # Checks that the request is POST.
    if request.POST:

        # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return get_json(404, failure_message)

        # Get validated data from POST request.
        event_id = request.POST.get('id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        try:
            event = Event.objects.get(id=int(event_id))
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
                guest = create_guest(event_id, email, first_name, last_name, phone)
                if isinstance(guest, Guest):
                    return attend_event(event_id, guest, charge.id)
                return get_json(201, 'Signed-up for the event!')
        except:
            return get_json(404, 'Payment not excepted')

    return get_json(404, 'Request must be POST.')


def waiting_list_event_guest(request):
    """Guest sign-up for the event's waiting list."""

    # Checks that the request is POST.
    if request.POST:

        # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return get_json(404, failure_message)

        # Get validated data from POST request.
        event_id = request.POST.get('id')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')

        # Sign-up to event as guest.
        try:
            guest = create_guest(event_id, email, first_name, last_name, phone)
            if isinstance(guest, Guest):
                return waiting_list_event(event_id, guest, None)
        # Couldn't sign up for the event.
        except:
            return get_json(400, "Could not sign up for the event.")

    return get_json(400, 'Request must be POST.')


def attend_event(event_id, attendee, payment_id):
    """Takes in a user or a guest and lets them attend the event."""

    # Gets the event.
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


def sign_off_event(event_id, attendee):
    """User sign-off for event"""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user is signed up for the event.
    if not event.user_attends(attendee):
        return get_json(400, 'You are already signed off the event.')
    # Sign-off the event.
    try:
        EventRegistration.objects.get(event=event, attendee=attendee).delete()

        if len(event.get_waiting_list() > 0):

            attendee, payment_id = event.waiting_list_next()
            attend_event(event_id, attendee, payment_id)

            if isinstance(attendee, User):
                EventWaitingList.objects.filter(event=event, attendee=attendee).delete()
            else:
                EventGuestWaitingList.objects.filter(event=event, attendee=attendee).delete()

        return get_json(201, 'Signed-off the event!')
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the event.")


def waiting_list_event(event_id, attendee, payment_id):
    """Takes in a user or a guest and lets them sign-up for the event's waiting list."""

    # Gets the event.
    event = Event.objects.get(id=event_id)

    # Checks whether the event has an attendance cap, and if so, if it's reached.
    if event.check_attendance_cap():
        return get_json(400, 'The event has reached its attendance cap.')
    # Check whether the event has an end date for registration, and if so, if it's exceeded.
    if not event.check_sign_up_end_date():
        return get_json(400, 'The event registration has ended.')

    try:
        # Sign-up for event as user.
        if isinstance(attendee, User):
            event.attend_waiting_list(attendee, payment_id, datetime.now())
        # Sign-up for event as guest.
        elif isinstance(attendee, Guest):
            event.guest_attend_waiting_list(attendee, payment_id, datetime.now())
        # Illegal argument, attendee is neither user nor guest.
        else:
            return get_json(400, "Attendee is neither user nor guest.")
    except:
        # Couldn't sign up for the event.
        return get_json(400, "Could not sign up for the waiting list.")

    # Sends confirmation mail after successfully signing-up for the event.
    return get_json(201, 'Signed-up for the waiting list!')


def sign_off_waiting_list(event_id, attendee):
    """User sign-off the event's waiting list."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user is signed up for the event.
    if not event.user_attends(attendee):
        return get_json(400, 'You are already signed off the event.')
    # Sign-off the event.
    try:
        EventWaitingList.objects.get(event=event, attendee=attendee).delete()

        return get_json(201, 'Signed-off the waiting list!')
    # Couldn't sign-off the event.
    except:
        return get_json(400, "Could not sign-off the waiting list.")


def validate_guest_data(data):
    """Validates the input data when attending event as a guest."""

    try:
        Event.objects.get(id=data.get('id'))
        validate_email(data.get('email'))
        validate_integer(data.get('phone'))
    except ValidationError as e:
        return e.message
    except Event.DoesNotExist:
        return _("Event dose not exist")
    return None


def create_guest(event_id, email, first_name, last_name, phone):
    """Creates a Guest object if the guest isn't already attending the event."""

    # Gets the event.
    event = Event.objects.get(id=event_id)

    # Checks if the guest already attends the event or is on the event's waiting list.
    guest_attends = EventGuestRegistration.objects.filter(event=event, attendee__email=email, attendee__first_name=first_name, attendee__last_name=last_name, attendee__phone_number=phone).exists()
    if guest_attends:
        return get_json(400, 'The guest is already attending the event.')

    # Checks if the guest is on the event's waiting list.
    guest_on_waiting_list = EventGuestWaitingList.objects.filter(event=event, attendee__email=email, attendee__first_name=first_name, attendee__last_name=last_name, attendee__phone_number=phone).exists()
    if guest_on_waiting_list:
        return get_json(400, 'The guest is already on the waiting list for the event.')

    # Gets the guest if the object already exists, else creates guest.
    guest = Guest.objects.get_or_create(email=email, first_name=first_name, last_name=last_name, phone_number=phone)

    return guest





