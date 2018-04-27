from datetime import datetime

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from django.utils import translation
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership
from . import create_event, get_events
from events.models.event import Event, EventDescription, EventRegistration, EventWaitingList
from events.models.sub_event import SubEvent, SubEventRegistration
from events.models.category import Category
from django.core.mail import send_mail
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


def attend_event(event_id, user, payment_id):
    """User: sign up for event."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user isn't signed up for the event.
    if not event.user_attends(user=user):
        # Checks that the event isn't capped out.
        if event.check_attendance_cap():
            # Free event.
            if not event.payment_required(payment_id=payment_id):
                try:
                    # Try to sign up for the event, without payment.
                    event.attend_event(attendee=user, registration_time=datetime.now())
                except:
                    # Failure JSON message, couldn't sign up for the event.
                    return get_json(400, "Couldn't sign up for event.")

            # Priced event.
            else:
                try:
                    # Try to sign up for the event, with payment.
                    event.attend_event(attendee=user, payment_id=payment_id, registration_time=datetime.now())
                except:
                    # Failure JSON message, couldn't sign up for the event.
                    return get_json(400, "Couldn't sign up for event.")

            # Send mail confirmation after successfully signing up for the event.
            event_send_mail(event, user)
            # Success JSON message.
            return get_json(201, 'You are now attending this event')
        # Failure JSON message, the event is capped out.
        return get_json(400, 'The event is capped out.')
    # Failure JSON message, the user is already signed up for the event.
    return get_json(400, 'Already signed up for this event.')


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


def sign_off_event(event_id, user):
    """User: sign off the event."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user is signed up for the event.
    if event.user_attends(user=user):
        try:
            # Try to sign off the event.
            EventRegistration.objects.get(event=event, attendee=user).delete()
            return get_json(201, 'You are now signed off the event.')
        except:
            # Failure JSON message, couldn't sign off the event.
            return get_json(400, "Couldn't sign off the event.")
    return get_json(400, 'You are already signed off the event.')


def waiting_list_event(event_id, user, payment_id):
    """User: sign up for the event's waiting list."""

    # Get event.
    event = Event.objects.get(id=event_id)

    # Checks that the user isn't already signed up for the event.
    if not event.user_attends(user=user):
        # Checks that the user isn't already on the event's waiting list.
        if event.user_on_waiting_list(user=user):
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
        # Failure JSON message, the user is already on the event's waiting list.
        return get_json(400, 'Already signed up for the waiting list.')
    # Failure JSON message, the user is already signed up for the event.
    return get_json(400, 'Already signed up for this event.')


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


def guest_attend_event(event_id, guest, payment_id):
    """Guest: sign up for event."""

    # Get event
    event = Event.objects.get(id=event_id)

    # Checks that the guest isn't signed up for the event.
    if not event.guest_attends(guest=guest):
        # Checks that the event isn't capped out.
        if event.check_attendance_cap():
            # Free event.
            if event.payment_required():
                try:
                    # Try to sign up for the event, without payment.
                    event.guest_attend_event(attendee=guest, registration_time=datetime.now())
                except:
                    # Failure JSON message, couldn't sign up for the event.
                    return get_json(400, "Couldn't sign up for event.")

            # Priced event.
            else:
                try:
                    # Try to sign up for the event, with payment.
                    event.user_attend_event(attendee=guest, payment_id=payment_id, registration_time=datetime.now())
                except:
                    # Failure JSON message, couldn't sign up for the event.
                    return get_json(400, "Couldn't sign up for event.")

            # Send mail confirmation after successfully signing up for the event.
            event_send_mail(event, guest)
            # Success JSON message.
            return get_json(201, 'You are now attending this event')
        # Failure JSON message, the event is capped out.
        return get_json(400, 'The event is capped out.')
    # Failure JSON message, the guest is already signed up for the event.
    return get_json(400, 'Already signed up for this event.')


def guest_waiting_list_event(event_id, guest, payment_id):
    """User event waiting list sign up"""

    # Get event
    event = Event.objects.get(id=event_id)

    # Checks that the guest isn't signed up for the event
    if not event.guest_attends(guest=guest):
        # Checks that the guest isn't on the event's waiting list
        if event.user_on_waiting_list(guest=guest):
            # Checks that the event is capped out.
            if not event.check_attendance_cap():
                # Free event.
                if not event.payment_required():
                    try:
                        # Try to sign up for the event, without payment.
                        event.guest_attend_waiting_list(attendee=guest, registration_time=datetime.now())
                    except:
                        # Failure JSON message, couldn't sign up for the event.
                        return get_json(400, "Couldn't sign up for event.")

                # Priced event.
                else:
                    try:
                        # Try to sign up for the event, with payment.
                        event.guest_attend_waiting_list(attendee=guest, payment_id=payment_id, registration_time=datetime.now())
                    except:
                        # Failure JSON message, couldn't sign up for the event.
                        return get_json(400, "Couldn't sign up for event.")

                # Success JSON message.
                return get_json(201, 'You are now signed up for the waiting list.')
            # Failure JSON message, the event is capped out.
            return get_json(400, 'The event is not capped out.')
        # Failure JSON message, the guest is already on the event's waiting list.
        return get_json(400, 'Already signed up for the waiting list.')
    # Failure JSON message, the user is already signed up for the event.
    return get_json(400, 'Already signed up for this event.')


