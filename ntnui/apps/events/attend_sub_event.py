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
