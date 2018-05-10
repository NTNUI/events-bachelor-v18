from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import translation

from events.models.category import Category
from events.models.event import Event
from events.models.sub_event import SubEvent

from .views import (get_json)


def get_events_request(request):
    return get_events(request, False)


def get_attending_events_request(request):
    return get_events(request, True)


def get_events(request, attending):
    """ Returns a set of events based on the requested sorting and filtering. """

    # Checks if the request is GET.
    if not request.method == "GET":
        return get_json(404, _('Request must be GET.'))

    # Gets the page from the request.
    # Gets 1, if the page is not given as a param in the url.
    page = request.GET.get('page', 1)

    events = get_filtered_events(request, attending)

    # Paginate the events, with 10 elements on every page.
    p = Paginator(events, 10)

    # Get JSON from the paginated events
    events = get_events_json(p.page(page))

    # Return the JSON also containing the page number and page count.
    return JsonResponse({
        'events': events,
        'page_number': page,
        'page_count': p.num_pages}
    )


def get_filtered_events(request, attending):
    """Returns all the events that fits the sort_by, search and filter_by"""

    # Get filters from params.
    sort_by = request.GET.get('sort-by', "")
    search = request.GET.get('search', "")
    filter_host = request.GET.get('filter-host', "")

    if not attending:
        events = get_filtered_on_search_events(search, False)
        events = get_filtered_events_on_host(filter_host, events)
        events = get_sorted_events(sort_by, events)

        return events

    else:
        events = get_filtered_on_search_events(search, True)
        events = get_filtered_events_on_host(filter_host, events)
        events = get_sorted_events(sort_by, events)

        attending_events = []

        # For each event.
        for event in events:

            # Checks if the event has categories.
            if Category.objects.filter(event=event).exists():
                sub_event_list = []
                categories = Category.objects.get(event=event)

                # Gets all the categories sub-events.
                for i in range(len(categories)):
                    sub_events = SubEvent.objects.filter(category=categories[i])

                    # Adds all the category's sub-events to the sub_event_list.
                    for sub_event in sub_events:
                        sub_event_list.append(sub_event)

                # For each sub-event.
                for sub_event in sub_event_list:

                    # Checks if the user attends the sub-event.
                    if sub_event.is_user_enrolled(request.user):

                        # Adds the event to the list of events which the user attends, if the user attends a sub-event.
                        if event not in attending_events:
                            attending_events.append(event)
            else:

                if event.is_user_enrolled(request.user):
                    attending_events.append(event)

        return attending_events


def get_filtered_on_search_events(search, attending):
    """ Filters all events on the given search. """

    if not attending:

        # Checks if the search have a value.
        if search is not None and search != '':

            # Search for the word in the event's name and descriptions.
            return Event.objects.filter(Q(eventdescription__language=translation.get_language()) &
                                        (Q(eventdescription__name__icontains=search) |
                                         Q(eventdescription__description_text__icontains=search) |
                                         Q(tags__name__icontains=search)))
        else:
            # if not search return all event objects
            return Event.objects.filter(eventdescription__language=translation.get_language())

    else:

        # Checks if the search have a value.
        if search is not None and search != '':

            # Search for the word in the event's name and descriptions.
            return Event.objects.filter(
                Q(end_date__gte=datetime.now()) & Q(eventdescription__language=translation.get_language()) &
                (Q(eventdescription__name__icontains=search) | Q(eventdescription__description_text__icontains=search) |
                 Q(tags__name__icontains=search)))
        else:
            # Returns all events when no search is specified.
            return Event.objects.filter(
                Q(end_date__gte=datetime.now()) & Q(eventdescription__language=translation.get_language()))


def get_filtered_events_on_host(hosts, events):
    """ Gets a list of events and filters it on the list of hosts. """

    # Returns the list of events without filtering, as no hosts are specified.
    if hosts == "":
        return events

    # Gets the list of hosts.
    host_list = hosts.split("-")

    # NTNUI is one of the hosts which gets filtered on.
    # Returns the list of events filtered on NTNUI and the sports groups in host_list.
    if 'NTNUI' in host_list:
        host_list.remove('NTNUI')
        return events.filter(Q(sports_groups__in=host_list) | Q(is_host_ntnui=True))
    else:
        # Returns the list of events filtered on the hosts.
        return events.filter(sports_groups__in=host_list)


def get_sorted_events(sort_by_criterion, events):
    """ Gets a list of events and sorts it by the given criterion. """

    # Criteria the events can be sorted by.
    sort_by_criteria = ['start_date', 'end_date', 'name']

    # Checks that sort_by_criteria has a valid value.
    if sort_by_criterion is not None:

        if (sort_by_criterion or sort_by_criterion[1:]) in sort_by_criteria:

            # Checks if the sorting is ascending or descending.
            sort_type = ''
            if sort_by_criterion[0] == '-':
                sort_type = '-'
                sort_by_criterion = sort_by_criterion[1:]

            # if the sort by is not in the event table we need to find the filed by merging
            if sort_by_criterion == 'name':
                sort_by_criterion = sort_type + 'eventdescription__name'

            # Returns the list of events, sorted by the criterion.
            return events.order_by(sort_by_criterion, 'start_date')
    else:
        # The sort_by_criterion does not match any of the sort_by_criteria.
        # Returns the list of events, sorted by the events' start_date.
        return events.order_by('start_date')


def get_events_json(events):
    """ Creates a list of dictionaries containing the events' information. """

    event_list = []

    for event in events:
        event_list.append({
            'id': event.id,
            'name': event.name(),
            'place': event.place,
            'description': event.description(),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'priority': event.priority,
            'host': event.get_host(),
            'cover_photo': str(event.cover_photo)
        })

    return event_list
