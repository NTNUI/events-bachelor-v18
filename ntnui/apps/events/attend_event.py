from datetime import datetime
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template, render_to_string
from events.models import Event, EventRegistration, Category, SubEvent, SubEventRegistration, Guest
from django.core.mail import send_mail


def get_json(code, message):
    """Returnes json with the given format"""
    return JsonResponse({
        'message': message},
        status=code)


@login_required
def add_attendance_to_event(request):
    """Adds attendance to the given event for the given user"""
    if request.POST:
        id = request.POST.get('id')
        return attend_event(int(id), request.user, None)
    return get_json(400, 'Request must be post')


def attend_event(id, user, payment_id):
    event = Event.objects.get(id=id)
    if event.attendance_cap is None or event.attendance_cap > event.get_attendees().count():
        if payment_id is not None or event.require_payment:
            # Checks that the user is not already attending
            if not EventRegistration.objects.filter(event=event, attendee=user).exists():
                try:
                    # Try to create a entry
                    if event.require_payment:
                        EventRegistration.objects.create(event=event, attendee=user, payment_id=payment_id,
                                                         registration_time=datetime.now())
                    else:
                        EventRegistration.objects.create(event=event, attendee=user,
                                                         registration_time=datetime.now())
                except:
                    return get_json(400, 'Could not add you to this event')
                event_send_mail(event, user)
                return get_json(201, 'You are now attending this event')
            return get_json(400, 'You are already attending this event')
        return get_json(400, 'You have to pay for this event')
    return get_json(400, 'Event has reached its maximum number of participants')


def create_guest():
    return 2


def attend_event_guest(id, user, payment_id):
    event = Event.objects.get(id=id)
    if event.attendance_cap is None or event.attendance_cap > event.get_attendees().count():
        if payment_id is not None or event.require_payment:
            # Checks that the user is not already attending
            if not EventRegistration.objects.filter(event=event, attendee=user).exists():
                try:
                    event.guest_attendees.add(create_guest())
                    # Try to create a entry
                    if event.require_payment:

                        EventRegistration.objects.create(event=event, attendee=user, payment_id=payment_id,
                                                         registration_time=datetime.now())
                    else:
                        EventRegistration.objects.create(event=event, attendee=user,
                                                         registration_time=datetime.now())
                except:
                    return get_json(400, 'Could not add you to this event')
                event_send_mail(event, user)
                return get_json(201, 'You are now attending this event')
            return get_json(400, 'You are already attending this event')
        return get_json(400, 'You have to pay for this event')
    return get_json(400, 'Event has reached its maximum number of participants')



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
def remove_attendance_from_event(request):
    """Remove the user from attending the given event """
    if request.POST:
        id = int(request.POST.get('id'))
        user = request.user
        return remove_attendance(id, user)
    return get_json(400, 'request is not post')


def remove_attendance(id, user):
    try:
        if EventRegistration.objects.filter(event__id=id, attendee=user).exists():
            registration = EventRegistration.objects.get(event__id=id, attendee=user)
            registration.delete()
            return get_json(201, 'You are no longer attedning this event')
        return get_json(400, 'Attendance does not exists')
    except:
        return get_json(400, 'Could not remove attendence')


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
                return get_json(200, 'You are now attending this event')
        except:
            return get_json(404, 'Payment not excepted')
    return get_json(404, 'Request must be post.')


def refund_event(request):
    print(request.POST.get('id'))
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
