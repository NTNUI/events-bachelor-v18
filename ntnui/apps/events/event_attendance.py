import uuid
from datetime import datetime

import pytz
import stripe
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email, validate_integer
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from events.models.event import (Event, EventGuestRegistration,
                                 EventGuestWaitingList, EventRegistration,
                                 EventWaitingList)
from events.models.guest import Guest
from events.models.sub_event import (SubEvent, SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)

from .views import (get_event_by_id, get_json, get_sub_event_by_id,
                    get_sub_events)

""" User and guest sign-up for events and sub-events. """


def attend_event_request(request):
    """ Lets users and guests sign up for events and sub-events, which are free to attend. """

    event, attendee, guest_created, eligible_to_attend_event, error_response = verify_sign_up(request, True)

    # Checks if the attendee is eligible to attend the event.
    # If there is created a new guest who can't attend the event, it gets deleted.
    if not eligible_to_attend_event:
        if guest_created:
            delete_guest(attendee)
        return error_response

    has_sub_events, error_response = event_has_sub_events(event)

    # Checks that the attendee does not attempt to sign up for an event which has sub-events.
    if has_sub_events:
        return error_response

    # Checks that the event is free to attend.
    elif event.is_payment_event():
        return get_json(400, 'The event requires payment to attend.')

    else:
        return attend_event(request, event, attendee, None)


def attend_payment_event_request(request):
    """ Lets users and guests sign up for events and sub-events, which require payment to attend. """

    event, attendee, guest_created, eligible_to_attend_event, error_response = verify_sign_up(request, True)

    # Checks if the attendee is eligible to attend the event.
    # If there is created a new guest who can't attend the event, it gets deleted.
    if not eligible_to_attend_event:
        if guest_created:
            delete_guest(attendee)
        return error_response

    # Checks that the event requires payment to attend.
    if not event.is_payment_event():
        return get_json(400, 'The event does not require payment to attend.')

    payment_id, payment_accepted, error_response = charge_card(request.POST, event, attendee)

    # Checks if the payment for the event is accepted.
    # If there is created a new guest and the payment is declined, it gets deleted.
    if not payment_accepted:
        if guest_created:
            delete_guest(attendee)
        return error_response

    return attend_event(request, event, attendee, payment_id)


def waiting_list_event_request(request):
    """ Lets users and guests sign up for events' and sub-events' waiting lists, which are free to attend. """

    event, attendee, guest_created, eligible_to_attend_event, error_response = verify_sign_up(request, False)

    # Checks if the attendee is eligible to attend the event.
    # If there is created a new guest who can't attend the event, it gets deleted.
    if not eligible_to_attend_event:
        if guest_created:
            delete_guest(attendee)
        return error_response

    # Checks that the event is free to attend.
    if event.is_payment_event():
        return get_json(400, 'The event requires payment to attend.')

    return waiting_list_event(request, event, attendee, None)


def attend_event(request, event, attendee, payment_id):
    """ Creates the event or sub-event registration for a user or a guest. """

    # Generates a token which uniquely identifies the registration.
    token = str(uuid.uuid4())

    # Lets a user attend either an event or sub-event.
    if isinstance(attendee, User):
        event.user_attend(attendee, payment_id, datetime.now(pytz.utc), token)

    # Lets a guest attend ether an event or a sub-event.
    elif isinstance(attendee, Guest):
        event.guest_attend(attendee, payment_id, datetime.now(pytz.utc), token)

    # The attendee given is neither a user nor a guest.
    else:
        return get_json(400, _('Only users and guests can attend events.'))

    # Sends an email confirming the event sign-up.
    attendance_mail(request, event, attendee, token)
    return JsonResponse({'message': _('Signed up for the event!'),
                         'number_of_participants': len(event.get_attendee_list()),
                         'attendance_cap': event.attendance_cap}, status=201)


def waiting_list_event(request, event, attendee, payment_id):
    """ Creates the event or sub-event waiting list registration for a user or a guest. """

    # Generates a token which uniquely identifies the registration.
    token = str(uuid.uuid4())

    # Lets a user attend either an event's or a sub-event's waiting list.
    if isinstance(attendee, User):
        event.user_attend_waiting_list(attendee, payment_id, datetime.now(pytz.utc), token)

    # Lets a guest attend either an event's or a sub-event's waiting list.
    elif isinstance(attendee, Guest):
        event.guest_attend_waiting_list(attendee, payment_id, datetime.now(pytz.utc), token)

    # The attendee given is neither a user nor a guest.
    else:
        return get_json(400, _('Only users and guests can attend events.'))

    # Sends an email confirming the waiting list sign-up,
    waiting_list_mail(request, event, attendee,  token)
    return JsonResponse({'message': _("Signed up for the event's waiting list!"),
                         'number_of_participants': len(event.get_attendee_list()),
                         'attendance_cap': event.attendance_cap}, status=201)


def verify_sign_up(request, event_has_open_spots):
    """ Checks that the user or guest who's trying to sign up for an event or sub-event is eligible to attend. """

    # Checks that the request is POST.
    if not request.POST:
        return None, None, False, False, get_json(400, _('Request must be POST.'))

    # An event will have 'event_id', while a sub-event will have 'sub_event_id'.
    event_id = request.POST.get('event_id')
    sub_event_id = request.POST.get('sub_event_id')

    # Gets the event or sub-event which the attendee is signing up to.
    if event_id:
        event = get_event_by_id(event_id)
    elif sub_event_id:
        event = get_sub_event_by_id(sub_event_id)
    else:
        return None, None, False, False, get_json(400, _('Cannot find the event ID.'))

    # The attendee is a user.
    if request.user.is_authenticated():

        # Gets the user.
        user = request.user

        # Checks if the user is a User object.
        if not isinstance(user, User):
            return event, None, False, False, get_json(400, _('The attendee is not a member.'))

        # Checks if the user attends the event already.
        elif event.is_user_enrolled(user):
            return event, user, False, False, get_json(400, _('The user already attends the event.'))

        # Checks if the user is on the event's waiting list already.
        elif event.is_user_on_waiting_list(user):
            return event, user, False, False, get_json(400, _('The user is on the waiting list.'))

        # Checks if the registration period has ended.
        elif event.is_registration_ended():
            return event, user, False, False, get_json(400, _('The event registration has ended.'))

        else:
            # Verifies event sign-up.
            # Checks that the event's attendance cap ain't exceeded, so the attendee can join the event.
            if event_has_open_spots:
                if not event.is_attendance_cap_exceeded():
                    return event, user, False, True, None
                else:
                    return None, None, False, False, get_json(400, _('The event is full.'))
            # Verify waiting list sign-up.
            # Checks that the event's attendance cap is exceeded, so the attendee can join the waiting list.
            else:
                if event.is_attendance_cap_exceeded():
                    return event, user, False, True, None
                else:
                    return None, None, False, False, get_json(400, _('The event still has open spots.'))

    else:
        # Validates the data from the guest sign-up form.
        error_response = validate_guest_data(request.POST)
        if error_response:
            return event, None, False, False, error_response

        # Either gets an existing guest matching the input form, or creates a new guest.
        guest, guest_created, error_response = get_or_create_guest(request.POST)

        # Checks if the guest is a Guest object.
        if not isinstance(guest, Guest):
            return event, guest, guest_created, False, get_json(400, _('The attendee is not a guest.'))
        # Checks if the guest attends the event already.
        elif event.is_guest_enrolled(guest):
            return event, guest, guest_created, False, get_json(400, _('The guest already attends the event.'))

        # Checks if the guest is on the event's waiting list already.
        elif event.is_guest_on_waiting_list(guest.id):
            return event, guest, guest_created, False, get_json(400, _('The guest is on the waiting list.'))

        # Checks if the registration period has ended.
        elif event.is_registration_ended():
            return event, guest, False, False, get_json(400, _('The event registration has ended.'))

        else:
            # Verifies event sign-up.
            # Checks that the event's attendance cap ain't exceeded, so the attendee can join the event.
            if event_has_open_spots:
                if not event.is_attendance_cap_exceeded():
                    return event, guest, guest_created, True, None
                else:
                    return event, guest, guest_created, False, get_json(400, _('The event is full.'))
            # Verifies waiting list sign-up.
            # Checks that the event's attendance cap is exceeded, so the attendee can join the waiting list.
            else:
                if event.is_attendance_cap_exceeded():
                    return event, guest, guest_created, True, None
                else:
                    return event, guest, guest_created, False, get_json(400, _('The event still has open spots.'))


def event_has_sub_events(event):
    """ Denies sign up to events which has sub-events. """

    if isinstance(event, Event):
        if len(get_sub_events(event)) > 0:
            return True, get_json(400, _('Cannot sign up for an event which has sub-events.'))
    return False, None


def charge_card(data, event, attendee):
    """ Charges the attendee's card. """

    # Requests the necessary data for creating the Stripe payment.
    amount = event.price * 100
    description = str(event.name()) + ' - ' + str(attendee)
    email = data.get('stripeEmail')
    token = data.get('stripeToken')
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Creates a payment with Stripe.
    try:
        payment = stripe.Charge.create(
            receipt_email=email, source=token, amount=amount, currency='NOK', description=description)
    # Catch exceptions.
    except stripe.error.CardError:
        return None, False, get_json(400, _('Payment declined.'))
    except stripe.error.RateLimitError:
        return None, False, get_json(400, _('Too many requests made to the API too quickly.'))
    except stripe.error.AuthenticationError:
        return None, False, get_json(400, _("Authentication with Stripe's API failed."))
    except stripe.error.APIConnectionError:
        return None, False, get_json(400, _('Network communication with Stripe failed.'))
    except stripe.error.StripeError:
        return None, False, \
               get_json(400, _('Something went wrong, try again later or contact the host if the problem persists.'))

    # Payment accepted.
    return payment.id, True, None


def validate_guest_data(data):
    """ Validates the data from the guest sign-up form. """

    try:
        # Checks that the event or sub-event which the guest is trying to sign-up to exists.
        event_id = data.get('event_id')
        sub_event_id = data.get('sub_event_id')
        if event_id:
            Event.objects.get(id=event_id)
        else:
            SubEvent.objects.get(id=sub_event_id)

        # Validates the email and phone input from the sign-up form.
        validate_email(data.get('email'))
        validate_integer(data.get('phone'))

    # Catch exceptions.
    except ValidationError as error:
        return get_json(404, error.message)
    except Event.DoesNotExist:
        return get_json(404, _('Event does not exist.'))
    except SubEvent.DoesNotExist:
        return get_json(404, _('Sub-event does not exist.'))

    # The input is valid.
    return None


def get_or_create_guest(data):
    """ Gets an existing guest or creates a new one. """

    # Request input data from the guest sign-up form.
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    phone = data.get('phone')

    # Checks if there exists a guest with identical input, or creates a new guest.
    try:
        guest, guest_created = Guest.objects.get_or_create(
            email=email, first_name=first_name, last_name=last_name, phone_number=phone)
    # Catch exceptions.
    except Guest.ValidationError:
        return None, False, get_json(400, _('Invalid input, cannot create guest.'))
    except Guest.MulitpleObjectsReturned:
        return None, False, get_json(400, _('There exists multiple identical guests.'))

    # Returns the guest and whether it was created or not.
    return guest, guest_created, None


def delete_guest(guest):
    """ Deletes the given guest. """

    if isinstance(guest, Guest):
        guest.delete()


def attendance_mail(request, event, attendee, token):
    """ Sends confirmation email to users and guests who signs up for events and sub-events. """

    # Mail header.
    sender, receiver, subject = create_mail_header(event, attendee)

    # Content for the mail body.
    content = {'user': attendee, 'event': event, 'request': request, 'token': token}

    # Mail body.
    message_plain = render_to_string('events/email/attendance.txt', content)
    message_html = render_to_string('events/email/attendance.html', content)

    # Sends email.
    send_mail(subject, message_plain, sender, receiver, html_message=message_html)


def waiting_list_mail(request, event, attendee, token):
    """ Sends confirmation email to users and guests who signs up for the waiting list of an event and sub-event. """

    # Mail header.
    sender, receiver, subject = create_mail_header(event, attendee)

    # Content for the mail body.
    content = {'user': attendee, 'event': event, 'request': request, 'token': token}

    # Mail body.
    message_plain = render_to_string('events/email/waiting_list.txt', content)
    message_html = render_to_string('events/email/waiting_list.html', content)

    # Sends email.
    send_mail(subject, message_plain, sender, receiver, html_message=message_html)


""" User and guest sign off for events and sub-events. """


def remove_attendance_request(request):
    """ Lets users sign off an event or sub-event, which are free to attend. """

    event, user, user_attends_event, user_on_waiting_list, error_response = verify_sign_off(request)

    # Checks that the user is signed up for the event or its waiting list.
    if not user_attends_event and not user_on_waiting_list:
        return error_response

    if user_attends_event:
        if isinstance(event, Event):
            # User is signed up for the event.
            attendance = EventRegistration.objects.get(event=event, attendee=user)

            # Deletes the event registration if the event is free to attend.
            if not attendance.payment_id:
                attendance.delete()
                waiting_list_next_attend(request, event)
                remove_attendance_email(event, user)
                return JsonResponse({'message': _('Signed off the event!'),
                                     'number_of_participants': len(event.get_attendee_list()),
                                     'attendance_cap': event.attendance_cap}, status=201)
        else:
            # User is signed up for the sub-event.
            attendance = SubEventRegistration.objects.get(sub_event=event, attendee=user)

            # Deletes the sub-event registration if the sub-event is free to attend.
            if not attendance.payment_id:
                attendance.delete()
                waiting_list_next_attend(request, event)
                remove_attendance_email(event, user)
                return JsonResponse({'message': _('Signed off the event!'),
                                     'number_of_participants': len(event.get_attendee_list()),
                                     'attendance_cap': event.attendance_cap}, status=201)

    else:
        if isinstance(event, Event):
            # User is signed up for the event's waiting list.
            waiting_list_registration = EventWaitingList.objects.get(event=event, attendee=user)

            # Deletes the waiting list registration if the event is free to attend.
            if not waiting_list_registration.payment_id:
                waiting_list_registration.delete()
                waiting_list_next_attend(request, event)
                remove_attendance_email(event, user)
                return JsonResponse({'message': _("Signed off the event's waiting list!"),
                                     'number_of_participants': len(event.get_attendee_list()),
                                     'attendance_cap': event.attendance_cap}, status=201)
        else:
            # User is signed up for the sub-event's waiting list.
            waiting_list_registration = SubEventWaitingList.objects.get(sub_event=event, attendee=user)

            # Deletes the waiting list registration if the sub-event is free to attend.
            if not waiting_list_registration.payment_id:
                waiting_list_registration.delete()
                waiting_list_next_attend(request, event)
                remove_attendance_email(event, user)
                return JsonResponse({'message': _("Signed off the event's waiting list!"),
                                     'number_of_participants': len(event.get_attendee_list()),
                                     'attendance_cap': event.attendance_cap}, status=201)

    # Can't sign off payment events.
    return get_json(400, _("Can't sign off payment events, contact the host for refunding."))


def remove_attendance_by_token_request(request, token):
    """ Lets users and guests sign off an event or sub-event, which are free to attend. """

    # Models which will be searched through for the token.
    search_models = [EventRegistration, EventWaitingList, EventGuestRegistration, EventGuestWaitingList,
                     SubEventRegistration, SubEventWaitingList, SubEventGuestRegistration, SubEventGuestWaitingList]
    search_results = []

    # Searches through the models for the token, and saves all results.
    for model in search_models:
        results = model.objects.filter(token=token)
        if results.exists():
            search_results.append(results)

    # No registrations matched the search.
    if len(search_results) == 0:
        return get_json(400, _('Found no matching event or sub-event registration.'))

    # One registration matched the search.
    elif len(search_results) == 1:

        registration = search_results[0].first()
        attendee = registration.attendee
        payment_id = registration.payment_id

        # Checks if the user or guest were signed up for an event or sub-event.
        if isinstance(registration, EventRegistration) or isinstance(registration, EventGuestRegistration):
            event = registration.event
        elif isinstance(registration, SubEventRegistration) or isinstance(registration, SubEventGuestRegistration):
            event = registration.sub_event
        else:
            event = None

        # Checks if the user or guest were signed up for an event's or sub-event's waiting list.
        if isinstance(registration, EventWaitingList) or isinstance(registration, EventGuestWaitingList):
            waiting_list = registration.event
        elif isinstance(registration, SubEventWaitingList) or isinstance(registration, SubEventGuestWaitingList):
            waiting_list = registration.sub_event
        else:
            waiting_list = None

        # Deletes the registration if it's related to an event or sub-event, which are free to attend.
        # Moves the next person on the waiting list into the list of attendees.
        if not payment_id:
            registration.delete()
            if event or waiting_list:
                remove_attendance_email(event, attendee)
                
                if event:
                    waiting_list_next_attend(request, event)
            return get_json(200, _('Signed off the event!'))

        # Can't sign off payment events.
        return get_json(400, _(' sign off payment events, contact the host for refunding.'))

    # Multiple registrations matched the search.
    else:
        return get_json(400, _('Found multiple matching registrations, contact the host to sign off the event.'))


def verify_sign_off(request):
    """ Checks that the user who's trying to sign off an event or sub-event is signed up beforehand. """

    # Checks that the request is POST.
    if not request.POST:
        return None, None, False, False, get_json(400, _('Request must be POST.'))

    # An event will have 'event_id', while a sub-event will have 'sub_event_id'.
    event_id = request.POST.get('event_id')
    sub_event_id = request.POST.get('sub_event_id')

    # Gets the event or sub-event which the attendee is signing up to.
    if event_id:
        event = get_event_by_id(event_id)
    elif sub_event_id:
        event = get_sub_event_by_id(sub_event_id)
    else:
        return None, None, False, False, get_json(400, _('Cannot find the event ID.'))

    # Checks that the user is logged in.
    if request.user.is_authenticated():

        # Gets the user.
        user = request.user

        # Checks if the user attends the event already.
        if event.is_user_enrolled(user):
            return event, user, True, False, None

        # Checks if the user is on the event's waiting list already.
        elif event.is_user_on_waiting_list(user):
            return event, user, False, True, None

        # The user isn't signed up for the event.
        else:
            return event, user, False, False, get_json(400, _('You are not signed up for this event.'))

    # The user have to log in to remove the attendance.
    else:
        return event, None, False, False, get_json(400, _('Please log in to sign off the event.'))


def waiting_list_next_attend(request, event):
    """ Gets the next person on the waiting list and signs them up for the event or sub-event. """

    # Checks that the event is free to attend.
    if event.is_payment_event():
        return

    # Checks if there are people on the waiting list.
    elif len(event.get_waiting_list()) > 0:

        # Gets the first person on the waiting list.
        attendee, payment_id = event.get_waiting_list_next()

        # The event or sub-event is free to attend, and there are not a payment ID in the waiting list registration.
        if not payment_id:

            if isinstance(event, Event):
                # Deletes the event waiting list registration for a user.
                if isinstance(attendee, User):
                    EventWaitingList.objects.filter(event=event, attendee=attendee).delete()
                # Deletes the event waiting list registration for a guest.
                else:
                    EventGuestWaitingList.objects.filter(event=event, attendee=attendee).delete()

            elif isinstance(event, SubEvent):
                # Deletes the sub-event waiting list registration for a user.
                if isinstance(attendee, User):
                    SubEventWaitingList.objects.filter(sub_event=event, attendee=attendee).delete()
                # Deletes the sub-event waiting list registration for a guest.
                else:
                    SubEventGuestWaitingList.objects.filter(sub_event=event, attendee=attendee).delete()

            # The event given to the function is neither a Event nor a SubEvent.
            else:
                return

            # The user or guest has been removed from the waiting list, and get moved into the event or sub-event.
            attend_event(request, event, attendee, None)

        # Can't move people into events or sub-events, where there are a payment ID in the waiting list registration.
        else:
            return


def remove_attendance_email(event, attendee):
    """ Sends confirmation email to users and guests who signs up for the waiting list of an event and sub-event. """

    # Mail header.
    sender, receiver, subject = create_mail_header(event, attendee)

    # Content for the mail body.
    content = {'user': attendee, 'event': event}

    # Mail body.
    message_plain = render_to_string('events/email/remove_attendance.txt', content)
    message_html = render_to_string('events/email/remove_attendance.html', content)

    # Sends email.
    send_mail(subject, message_plain, sender, receiver, html_message=message_html)


""" Generic functions applicable to both sign up and sign off. """


def create_mail_header(event, attendee):
    """ Gets the from, to, and subject fields for the email. """

    # Create mail header.
    sender = 'noreply@mg.ntnui.no'
    receiver = [attendee.email]
    subject = event.name() + ' - ' + ' - '.join(str(item) for item in event.get_host())

    # Returns the sender and receiver of the email and the email's subject.
    return sender, receiver, subject
