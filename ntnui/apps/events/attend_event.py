import stripe
from datetime import datetime

from .views import (get_json, get_event_by_id, get_sub_event_by_id)
from accounts.models import User
from events.models.guest import Guest
from events.models.event import Event, EventRegistration, EventWaitingList, EventGuestWaitingList, EventGuestRegistration
from events.models.sub_event import SubEvent

from django.conf import settings
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.core.validators import validate_email, validate_integer


""" Attend both free- and payment events and sub-events for users and guests. """


def attend_event_request(request):
    """User and guest sign-up for a free event."""

    event, attendee, guest_created, eligible_to_attend_event, error_message = verify_sign_up(request, True)

    if not eligible_to_attend_event:
        if guest_created:
            attendee.delete()
        return error_message

    return attend_event(event, attendee, None)


def attend_payment_event_request(request):
    """User and guest sign-up for a payment event."""

    event, attendee, guest_created, eligible_to_attend_event, error_message = verify_sign_up(request, True)

    if not eligible_to_attend_event:
        if guest_created:
            attendee.delete()
        return error_message

    charge, accepted, error_message = charge_card(request.POST, event, attendee)

    if not accepted:
        if guest_created:
            attendee.delete()
        return error_message

    return attend_event(event, attendee, charge)


def waiting_list_event_request(request):
    """User and guest sign-up for a free event's waiting list."""

    event, attendee, guest_created, eligible_to_attend_event, error_message = verify_sign_up(request.POST, False)

    if not eligible_to_attend_event:
        if guest_created:
            attendee.delete()
        return error_message

    return waiting_list_event(event, attendee, None)


def waiting_list_payment_event_request(request):
    """User and guest sign-up for a payment event."""

    event, attendee, guest_created, eligible_to_attend_event, error_message = verify_sign_up(request, False)

    if not eligible_to_attend_event:
        if guest_created:
            attendee.delete()
        return error_message

    charge, accepted, error_message = charge_card(request.POST, event, attendee)

    if not accepted:
        if guest_created:
            attendee.delete()
        return error_message

    return waiting_list_event(event, attendee, charge)


def attend_event(event, attendee, payment_id):
    """"""

    if isinstance(attendee, User):
        event.user_attend(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        event.guest_attend(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Only users and guests can attend.")

    event_send_mail(event, attendee)
    return get_json(201, 'Signed-up for the event!')


def waiting_list_event(event, attendee, payment_id):
    """"""

    if isinstance(attendee, User):
        event.user_attend_waiting_list(attendee, payment_id, datetime.now())
    elif isinstance(attendee, Guest):
        event.guest_attend_waiting_list(attendee, payment_id, datetime.now())
    else:
        return get_json(400, "Only users and guests can attend.")

    return get_json(201, 'Signed-up for the waiting list!')


def verify_sign_up(request, event_has_open_spots):
    """"""

    # Checks that the request is POST.
    if not request.POST:
        return None, None, False, False, get_json(400, 'Request must be POST.')

    # Gets the event.
    event_id = request.POST.get('event_id')
    sub_event_id = request.POST.get('sub_event_id')
    if event_id:
        event = get_event_by_id(event_id)
    else:
        event = get_sub_event_by_id(sub_event_id)

    # Checks if the event's registration has ended.
    if event.is_registration_ended():
        return None, None, False, False, get_json(400, 'The event registration has ended.')

    if request.user.is_authenticated():

        # Gets the user.
        user = request.user

        if not isinstance(user, User):
            return None, None, False, False, get_json(400, 'The attendee is not a user.')
        # Checks if the user already attends the event.
        elif event.is_user_enrolled(user):
            return None, None, False, False, get_json(400, 'The user already attends the event.')
        # Checks if the user is on the event's waiting list.
        elif event.is_user_on_waiting_list(user):
            return None, None, False, False, get_json(400, 'The user is on the waiting list.')
        # The user can attend the event.
        else:
            if event_has_open_spots:
                if not event.is_attendance_cap_exceeded():
                    return event, user, False, True, None
                else:
                    return None, None, False, False, get_json(400, 'The event is full.')
            else:
                if event.is_attendance_cap_exceeded():
                    return event, user, False, True, None
                else:
                    return None, None, False, False, get_json(400, 'The event still has open spots.')

    else:

        # Validates the input from the guest sign-up form, and gives error messages for invalid fields.
        failure_message = validate_guest_data(request.POST)
        if failure_message:
            return None, None, False, False, get_json(404, failure_message)

        # Creates or gets the event the guest.
        guest, guest_created = get_or_create_guest(request)

        if not isinstance(guest, Guest):
            return event, guest, guest_created, False, get_json(400, 'The attendee is not a guest.')
        # Checks if the guest already attends the event.
        if event.is_guest_enrolled(guest):
            return event, guest, guest_created, False, get_json(400, 'The guest already attends the event.')
        # Checks if the guest is on the event's waiting list.
        elif event.is_guest_on_waiting_list(guest.id):
            return event, guest, guest_created, False, get_json(400, 'The guest is on the waiting list.')
        # The guest can attend the event.
        else:
            if event_has_open_spots:
                if not event.is_attendance_cap_exceeded():
                    return event, guest, guest_created, True, None
                else:
                    return event, guest, guest_created, False, get_json(400, 'The event is full.')
            else:
                if event.is_attendance_cap_exceeded():
                    return event, guest, guest_created, True, None
                else:
                    return event, guest, guest_created, False, get_json(400, 'The event still has open spots.')


def validate_guest_data(data):
    """"""

    try:
        event_id = data.get('event_id')
        sub_event_id = data.get('sub_event_id')
        if event_id:
            Event.objects.get(id=event_id)
        else:
            SubEvent.objects.get(id=sub_event_id)
        validate_email(data.get('email'))
        validate_integer(data.get('phone'))
    except ValidationError as error:
        return error.message
    except Event.DoesNotExist:
        return "Event doesn't exist."
    except SubEvent.DoesNotExist:
        return "Sub-event doesn't exist."
    return None


def get_or_create_guest(data):
    """"""

    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')

    try:
        guest, guest_created = Guest.objects.get_or_create(email=email, first_name=first_name, last_name=last_name,
                                                           phone_number=phone)
        return guest, guest_created
    except:
        return get_json(404, "Couldn't get or create the guest.")


def charge_card(data, event, attendee):
    """"""

    amount = event.price * 100
    description = str(event.name()) + " - " + str(attendee)
    email = data.get('stripeEmail')
    token = data.get('stripToken')
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        charge = stripe.Charge.create(receipt_email=email, source=token, amount=amount,
                                      currency="NOK", description=description)
    except:
        return None, False, get_json(400, "Payment not accepted")

    return charge.id, True, None


""" Remove attendance from free- and payment events and sub-events for users. """


def remove_attendance_request(request):
    """User: Sign-off for an event."""

    event, attendee, attending_event, on_waiting_list, error_message = verify_sign_off(request)

    if not attending_event and not on_waiting_list:
        return error_message

    if attending_event:

        if isinstance(attendee, User):
            payment_id = EventRegistration.objects.get(event=event, attendee=attendee).payment_id

            if payment_id:
                refunded, error_message = refund_event(payment_id)

                if refunded:
                    event.user_attendance_delete(attendee)
                    waiting_list_next_attend(event)
                    return get_json(200, 'You are refunded.')
                else:
                    return error_message

            else:
                event.user_attendance_delete(attendee)
                waiting_list_next_attend(event)
                return get_json(200, 'Not attending any more.')

    else:
        if isinstance(attendee, User):

            payment_id = EventWaitingList.objects.get(event=event, attendee=attendee).payment_id

            if payment_id:

                refunded, error_message = refund_event(payment_id)

                if refunded:
                    event.user_waiting_list_delete(attendee)
                    return get_json(200, 'You are refunded.')
                else:
                    return error_message

            else:
                event.user_waiting_list_delete(attendee)
                return get_json(200, 'Not attending any more.')

    return get_json(400, "Guest can't sign-off event' yet.")


def verify_sign_off(request):
    """"""

    # Checks that the request is POST.
    if not request.POST:
        return None, None, False, False, get_json(400, 'Request must be POST.')

    # Gets the event.
    event_id = request.POST.get('event_id')
    sub_event_id = request.POST.get('sub_event_id')
    if event_id:
        event = get_event_by_id(event_id)
    else:
        event = get_sub_event_by_id(sub_event_id)

    if request.user.is_authenticated():

        # Gets the user.
        user = request.user

        if not isinstance(user, User):
            return None, None, False, False, get_json(400, 'The attendee is not a user.')
        # Checks if the user already attends the event.
        elif event.is_user_enrolled(user):
            return event, user, True, False, None
        # Checks if the user is on the event's waiting list.
        elif event.is_user_on_waiting_list(user):
            return event, user, False, True, None
        # Checks if the event's registration has ended.
        if event.is_registration_ended():
            return event, None, False, False, get_json(400, 'Registration has ended, cannot sign off.')
        else:
            return event, user, False, False, get_json(400, 'Already signed off the event.')

    else:
        return None, None, False, False, get_json(400, 'Cannot sign off as guest yet.')


def refund_event(payment_id):

    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        stripe.Refund.create(
            charge=payment_id
        )
    except:
        return False, get_json("Refund failed.")
    
    return True, None


def waiting_list_next_attend(event):

    if len(event.get_waiting_list()) > 0 and not event.is_payment_event():

        attendee, payment_id = event.waiting_list_next()

        if isinstance(attendee, User):
            EventWaitingList.objects.filter(event=event, attendee=attendee).delete()
        else:
            EventGuestWaitingList.objects.filter(event=event, attendee=attendee).delete()

        attend_event(event, attendee, payment_id)


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
