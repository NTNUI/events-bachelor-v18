from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import translation
from django.utils.translation import gettext as _

from events.models.category import Category, CategoryDescription
from events.models.event import (Event, EventDescription,
                                 EventGuestRegistration, EventGuestWaitingList,
                                 EventRegistration, EventWaitingList)
from events.models.sub_event import (SubEvent, SubEventDescription,
                                     SubEventGuestRegistration,
                                     SubEventGuestWaitingList,
                                     SubEventRegistration, SubEventWaitingList)
from groups.models import Board, SportsGroup
from hs.models import MainBoardMembership

from . import get_events

def get_main_page(request):
    """ Returns the events' main page. """

    # Used to find out if the create-event button shall be rendered or not
    if request.user.is_authenticated:
        can_create_event = can_user_create_event(request.user)
    else:
        can_create_event = False

    # Get groups that are hosting events
    groups = SportsGroup.objects.filter(event__in=Event.objects.all()).distinct()

    return render(request, 'events/events_main_page.html', {
        'can_create_event': can_create_event,
        'groups': groups,
    })


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
            registration_end_date = None

        category_id = request.POST.get("category", "")

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

        SubEventDescription.objects.create(sub_event=sub_event, name=name_nb, custom_email_text=email_text_nb,
                                           language='nb')
        SubEventDescription.objects.create(sub_event=sub_event, name=name_en, custom_email_text=email_text_en,
                                           language='en')
        return JsonResponse({
            'id': sub_event.id,
            'message': _('New sub-event successfully created!')},
            status=201)


def get_remove_attendance_page(request, token):

    return render(request, 'events/remove_attendance.html')




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
        'waiting_list': item.is_attendance_cap_exceeded(),
        'is_user_on_waiting_list': item.is_user_on_waiting_list(request.user),
        'number_of_participants': len(item.get_attendee_list()),
        'attendance_cap': item.attendance_cap,
        'is_registration_ended': item.is_registration_ended(),
        'registration_end_date': item.registration_end_date,
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

    number_of_subevents = len(sub_event_list)

    # Checks if the user is sign in.
    if request.user.is_authenticated:
        attends = event.is_user_enrolled(request.user)
        can_create_event = can_user_create_event(request.user)
    else:
        # Returns false if not
        attends = False

    if request.user.is_authenticated:
        can_create_event = can_user_create_event(request.user)
    else:
        can_create_event = False

    waiting_list = event.is_attendance_cap_exceeded()
    is_user_on_waiting_list = event.is_user_on_waiting_list(request.user);

    if request.user.is_authenticated:
        if is_user_in_main_board(request.user):
            is_in_mainboard = is_user_in_main_board(request.user)
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
        'waiting_list': waiting_list,
        'is_user_on_waiting_list': is_user_on_waiting_list,
        'number_of_participants': len(event.get_attendee_list()),
        'attendance_cap': event.attendance_cap,
        'is_registration_ended': event.is_registration_ended(),
        'price': event.price,
        'registration_end_date': event.registration_end_date,
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
        can_create_event = can_user_create_event(request.user)
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
        eventregistrations = EventRegistration.objects.filter(event=event)
        eventwaitinglists = EventWaitingList.objects.filter(event=event)
        eventguestwaitinglists = EventGuestWaitingList.objects.filter(event=event)
        eventguestregistrations = EventGuestRegistration.objects.filter(event=event)
        if Category.objects.filter(event=event).exists():
            categories = Category.objects.filter(event=event)
            #print("Categories before deletion: " + categories)
            for category in categories:
                delete_category(category)
            #print("Categories after deletion: " + categories)

        if eventregistrations:
            for eventregistration in eventregistrations:
                eventregistration.delete()
        if eventguestregistrations:
            for eventguestregistration in eventguestregistrations:
                eventguestregistration.delete()
        if eventwaitinglists:
            for eventwaitinglist in eventwaitinglists:
                eventwaitinglist.delete()
        if eventguestwaitinglists:
            for eventguestwaitinglist in eventguestwaitinglists:
                eventguestwaitinglist.delete()

        # if eventregistration.payment_id != '':
        #    refund_event(request)
        eventdescription_no.delete()
        eventdescription_en.delete()
        event.delete()
    except:
        return get_json(400, "Could not delete event")

    return render(request, 'events/delete_event_page.html')

def delete_category_request(request):
    category = Category.objects.get(id=int(request.POST.get('id')))

    return delete_category(category)

def delete_category(category):
    try:
        print(category)
        categorydescription_nb = CategoryDescription.objects.get(category=category, language='nb')
        categorydescription_en = CategoryDescription.objects.get(category=category, language='en')

        if SubEvent.objects.filter(category=category).exists():
            subevents = SubEvent.objects.filter(category=category)
            for subevent in subevents:
                delete_subevent(subevent)
        categorydescription_nb.delete()
        categorydescription_en.delete()
        category.delete()

    except:
        return get_json(400, "Could not delete category")

    return get_json(200, "Category deleted")

def delete_subevent_request(request):
    subevent = SubEvent.objects.get(id=int(request.POST.get('id')))

    return delete_subevent(subevent)


def delete_subevent(subevent):
    try:
        subeventdescription_nb = SubEventDescription.objects.get(sub_event=subevent, language='nb')
        subeventdescription_en = SubEventDescription.objects.get(sub_event=subevent, language='en')
        subeventregistrations = SubEventRegistration.objects.filter(sub_event=subevent)
        subeventwaitinglists = SubEventWaitingList.objects.filter(sub_event=subevent)
        subeventguestregistrations = SubEventGuestRegistration.objects.filter(sub_event=subevent)
        subeventguestwaitinglists = SubEventGuestWaitingList.objects.filter(sub_event=subevent)

        if subeventregistrations:
            for subeventregistration in subeventregistrations:
                subeventregistration.delete()
        if subeventguestregistrations:
            for subeventguestregistration in subeventguestregistrations:
                subeventguestregistration.delete()
        if subeventwaitinglists:
            for subeventwaitinglist in subeventwaitinglists:
                subeventwaitinglist.delete()
        if subeventguestwaitinglists:
            for subeventguestwaitinglist in subeventguestwaitinglists:
                subeventguestwaitinglist.delete()
        subeventdescription_nb.delete()
        subeventdescription_en.delete()
        subevent.delete()

    except:
        return get_json(400, "Could not delete subevent")

    return get_json(200, "Subevent deleted")


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

    registration_end_date = ""
    if event.registration_end_date != "" and event.registration_end_date is not None:
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
        registration_end_date = data['registration_end_date']
        host = data['host']
        attendance_cap = data['attendance_cap']
        price = data['price']

        event.start_date = start_date
        event.end_date = end_date
        if registration_end_date == "":
            event.registration_end_date = None
        else:
            event.registration_end_date = registration_end_date
        if attendance_cap == "":
            event.attendance_cap = None
        else:
            event.attendance_cap = attendance_cap
        if price == "":
            event.price = None
        else:
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

        return JsonResponse({
            'message': "Edit event successful",
            'id': data['id']
        }, status=200)


def edit_category(request):
    if request.method == 'POST':
        data = request.POST
        try:
            categoryname_no = data['name_nb']
            categoryname_en = data['name_en']

            category = Category.objects.get(id=int(data['id']))

            categorydescription_no = CategoryDescription.objects.get(category=category, language='nb')
            categorydescription_en = CategoryDescription.objects.get(category=category, language='en')
            categorydescription_no.name = categoryname_no
            categorydescription_en.name = categoryname_en
            categorydescription_no.save()
            categorydescription_en.save()

            return JsonResponse({
                'message': "Edit category successful",
                'id': data['id']
            }, status=200)


        except:
            return get_json(400, "Edit category failed")


def edit_subevent(request):
    if request.method == 'POST':
        data = request.POST

        try:
            name_no = data['name_nb']
            name_en = data['name_en']
            email_text_no = data['email_nb']
            email_text_en = data['email_en']
            start_date = data['start_date']
            end_date = data['end_date']
            registration_end_date = data['registration_end_date']
            attendance_cap = data['attendance_cap']
            price = data['price']

            subevent = SubEvent.objects.get(id=int(data['id']))

            subevent.start_date = start_date
            subevent.end_date = end_date
            if registration_end_date == "":
                subevent.registration_end_date = None
            else:
                subevent.registration_end_date = registration_end_date
            if attendance_cap == "":
                subevent.attendance_cap = None
            else:
                subevent.attendance_cap = attendance_cap
            if price == "":
                subevent.price = None
            else:
                subevent.price = price

            subevent.save()
            subeventdescription_no = SubEventDescription.objects.get(sub_event=subevent, language='nb')
            subeventdescription_en = SubEventDescription.objects.get(sub_event=subevent, language='en')

            subeventdescription_no.name = name_no
            subeventdescription_en.name = name_en
            if email_text_no == "":
                subeventdescription_no.custom_email_text = None
            else:
                subeventdescription_no.custom_email_text = email_text_no
            if email_text_en == "":
                subeventdescription_en.custom_email_text = None
            else:
                subeventdescription_en.custom_email_text = email_text_en
            subeventdescription_no.save()
            subeventdescription_en.save()

            return get_json(200, "Edit subevent successful")

        except:
            return get_json(400, "Edit subevent failed")


def get_events_request(request):
    return get_events.get_events(request, False)


def get_attending_events_request(request):
    return get_events.get_events(request, True)


def get_event_attendees_page(request, id, numberofsubevents):
    event = Event.objects.get(id=int(id))

    if int(numberofsubevents) == 0:
        subeventsexist = False
        eventregistrations = EventRegistration.objects.filter(event=event)

        attendees = []
        for registration in eventregistrations:
            user = registration.attendee
            attendees.append(user.get_full_name())

        attendees.sort()

        context = {
            'subeventsexist': subeventsexist,
            'event': event,
            'attendees_list': attendees,
        }

    else:
        subeventsexist = True
        eventcategories = Category.objects.filter(event=event)

        subeventslist = []
        for category in eventcategories:
            subevents = SubEvent.objects.filter(category=category)
            for subevent in subevents:
                subeventslist.append(subevent)

        subevents_attendees_and_names_list = []

        for subevent in subeventslist:
            attendees = []
            users = []
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
                'event': event,
                'subevents_attendees_and_name_list': subevents_attendees_and_names_list,
            }

    return render(request, 'events/event_attendees_page.html', context)


@login_required
def edit_event_request(request):
    return edit_event(request)


@login_required
def get_create_event_page(request):
    """Returns the page where events are created"""

    # Checks if a user can create an event
    groups = get_groups_user_can_create_events_for(request.user)

    return render(request, 'events/create_new_event.html', {'groups': groups})





def get_groups_user_can_create_events_for(user):
    """Finds the groups a user can create events for"""

    # Create an empty return list
    return_list = []

    # Adds NTNUI if member of hs
    if is_user_in_main_board(user):
        return_list.append({'id': "NTNUI", 'name': 'NTNUI'})

    # Finds all the groups were the user is in the board
    for board in Board.objects.filter(president=user) | \
            Board.objects.filter(vice_president=user) | \
            Board.objects.filter(cashier=user):

        # Checks that the board is active
        for group in SportsGroup.objects.filter(active_board=board):
            return_list.append(group)

    return return_list




def event_has_description_and_name(description, name):
    """Checks that a description is not empyt"""
    if description is None or description.replace(' ', '') == "":
        return False, 'Event must have description'
    elif name is None or name.replace(' ', '') == "":
        return False, _('Event must have a name')
    return True, None


def get_json(code, message):
    """Returns JSON with the given format."""
    return JsonResponse({
        'message': message},
        status=code)


def get_event(request, id):
    if Event.objects.filter(id=int(id)).exists():
        event = Event.objects.get(id=int(id))

        categories_list = []
        if Category.objects.filter(event=event).exists():
            categories = Category.objects.filter(event=event).values()
            # for every category do:
            for i in range(len(categories)):
                # get all the sub-events for that category
                categories[i]['descriptions'] = list(
                    CategoryDescription.objects.filter(category__id=categories[i]['id']).values())
                categories[i]['sub-events'] = list(SubEvent.objects.filter(category__id=categories[i]['id']).values())
                for j in range(len(categories[i]['sub-events'])):
                    # Give subevents the right format
                    sub_event = categories[i]['sub-events'][j]
                    sub_event['start_date'] = '{:%Y-%m-%dT%H:%M}'.format(sub_event['start_date'])
                    sub_event['end_date'] = '{:%Y-%m-%dT%H:%M}'.format(sub_event['end_date'])
                    if sub_event['registration_end_date'] is not None and sub_event['registration_end_date'] != "":
                        sub_event['registration_end_date'] = '{:%Y-%m-%dT%H:%M}'.format(
                            sub_event['registration_end_date'])
                    sub_event['descriptions'] = list(
                        SubEventDescription.objects.filter(sub_event__id=sub_event['id']).values())
                categories_list.append(categories[i])

        return JsonResponse({
            'id': event.id,
            'name': event.name(),
            'place': event.place,
            'descriptions': list(EventDescription.objects.filter(event=event).values()),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'priority': event.priority,
            'price': event.price,
            'host': event.get_host(),
            'cover_photo': str(event.cover_photo),
            'categories': list(categories_list),
        })
    return get_json(404, "Event with id: " + id + " does not exist.")


def can_user_create_event(user):
    """ Checks if the user can create event of any kind"""

    # Checks if the user is a member of the main board.
    if is_user_in_main_board(user):
        return True

    # Checks if the user is in a member of any active boards.
    for board in (Board.objects.filter(Q(president=user) | Q(vice_president=user) | Q(cashier=user))):

        # Checks that the board which the user is a member of is active.
        if SportsGroup.objects.filter(active_board=board).exists():
            return True

    # The user is not eligible to create events.
    return False


def is_user_in_main_board(user):
    """ Checks if the user is a member of the main board. """

    return MainBoardMembership.objects.filter(person_id=user).exists()


def is_user_in_board(board, user):
    """ Checks if the user is a member of the board. """

    return board.president == user or board.vice_president == user or board.cashier == user
