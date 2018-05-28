from datetime import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import translation
from django.utils.translation import gettext as _

from events.models.event import Event

from .views import get_json, get_sub_events


def get_events_request(request):
    """ Gets the events which match the search, sorting, and filtering. """

    return get_events(request, False)


def get_attending_events_request(request):
    """ Gets the events which the user is signed up for and matches the search, sorting, and filtering. """

    return get_events(request, True)


def get_events(request, attending):
    """ Returns a set of events based on the requested sorting and filtering. """

    # Checks if the request is GET.
    if not request.method == "GET":
        return get_json(404, _('Request must be GET.'))

    # Gets the page from the request.
    # Gets 1, if the page is not given as a parameter in the url.
    page = request.GET.get('page', 1)

    # Gets the searched, sorted, and filtered events.
    # If attending is True, it only returns events which the user attends.
    events = get_filtered_events(request, attending)

    # Paginates the events, with 10 elements on each page.
    p = Paginator(events, 10)

    # Gets JSON from the paginated events.
    events = get_events_json(p.page(page))

    # Returns the JSON which also contains the page number and page count.
    return JsonResponse({'events': events, 'page_number': page, 'page_count': p.num_pages})


def get_filtered_events(request, attending):
    """ Returns all the events that fits the search, sorting, and filtering. """

    # Gets filters from the params.
    search = request.GET.get('search', "")
    sort_by = request.GET.get('sort-by', "")
    filter_host = request.GET.get('filter-host', "")

    # Gets all events which matches the search, sorting and filtering.
    if not attending:
        events = get_filtered_on_search_events(search, False)
        events = get_filtered_events_on_host(filter_host, events)
        events = get_sorted_events(sort_by, events)

        return events

    # Gets all events which the user attends and matches the search, sorting and filtering.
    else:
        events = get_filtered_on_search_events(search, True)
        events = get_filtered_events_on_host(filter_host, events)
        events = get_sorted_events(sort_by, events)

        attending_events = []

        for event in events:
            # Adds the event to attending_events if the user attends it.
            if event.is_user_enrolled(request.user):
                attending_events.append(event)

            else:
                sub_events = get_sub_events(event)

                # Adds the sub-events' main event to attending_events if the user attends one of them.
                for sub_event in sub_events:
                    if sub_event.is_user_enrolled(request.user):
                        attending_events.append(event)
                        break

        return attending_events


def get_filtered_on_search_events(search, attending):
    """ Filters all events on the given search. """

    # Checks if the search has a value and does the search on the events' name, description and tags.
    if search:
        events = Event.objects.filter(Q(eventdescription__language=translation.get_language()) &
                                      (Q(eventdescription__name__icontains=search) |
                                       Q(eventdescription__description_text__icontains=search) |
                                       Q(tags__name__icontains=search)))

    # Gets all events, as no search is given.
    else:
        events = Event.objects.filter(eventdescription__language=translation.get_language())

    # Returns all events given by the search.
    if not attending:
        return events

    # Returns the events given by the search which have not ended.
    else:
        return events.filter(end_date__gte=datetime.now())


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
    if sort_by_criterion and (sort_by_criterion in sort_by_criteria or sort_by_criterion[1:] in sort_by_criteria):
        # Checks if the sorting is ascending or descending.
        sort_type = ''
        if sort_by_criterion == '-name':
            sort_type = '-'
            sort_by_criterion = sort_by_criterion[1:]

        # If the sort by is not in the event table we need to find the field by merging.
        if sort_by_criterion == 'name':
            sort_by_criterion = sort_type + 'eventdescription__name'
        # Returns the list of events, sorted by the criterion.
        return events.order_by(sort_by_criterion, 'start_date')
    else:
        # The sort_by_criterion does not match any of the sort_by_criteria.
        # Returns the list of events, sorted by the events' start_date.
        return events.order_by('start_date')


def get_events_json(events):
    """ Gets a list of events and creates a list of dictionaries containing the events' information. """

    event_list = []

    # Creates dictionaries for each event and adds them to the event_list.
    for event in events:
        event_list.append({
            'id': event.id,
            'name': event.name(),
            'place': event.place,
            'price': event.price,
            'description': event.description(),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'priority': event.priority,
            'host': event.get_host(),
            'cover_photo': str(event.cover_photo)
        })

    return event_list
