from django.core.paginator import Paginator
from django.http import JsonResponse

from events.models import Event
from django.db.models import Q
from django.utils import translation


def get_events(request):
    """Returnes a set of events filter after the parms in the request"""
    if request.method == "GET":
        # gets the page from the request, or returns one if page is not given as a parm in the url
        page = request.GET.get('page', 1)
        events = get_filtered_events(request)

        # paginate the events, with 10 elements on every page
        p = Paginator(events, 10)

        # Get json from the paginated events
        events = get_events_json(p.page(page))

        # Return the json also containing the page number and page count
        return JsonResponse({
            'events': events,
            'page_number': page,
            'page_count': p.num_pages}
        )

    #if not get return 404
    return JsonResponse({
        'message': 'must be get'
    }, status=404)


def get_filtered_events(request):
    """Returnes all the events that fits the order_by, search and filter_by"""

    # Get filters from parms
    sort_by = request.GET.get('sort-by', "")
    search = request.GET.get('search', "")
    filter_host = request.GET.get('filter-host', "")

    # Filter the events
    events = get_filtered_on_search_events(search)
    events = get_filtered_on_host_events(filter_host, events)
    events = get_sorted_events(sort_by, events)

    # return the filtered events
    return events


def get_filtered_on_search_events(search):
    # Checks if search have a value
    if search is not None and search != '':
        # serach for the word in descriptions and name
        return Event.objects.filter(Q(eventdescription__language=translation.get_language()) &
                                      (Q(eventdescription__name__icontains=search) |
                                       Q(eventdescription__description_text__icontains=search) |
                                       Q(tags__name__icontains=search)))
    else:
        # if not search return all event objects
        return Event.objects.filter(eventdescription__language=translation.get_language())


def get_filtered_on_host_events(filter_host, events):
    if filter_host == "":
        return events
    host_list = filter_host.split("-")
    if 'NTNUI' in host_list:
        host_list.remove('NTNUI')
        return events.filter(Q(sports_groups__in=host_list) | Q(is_host_ntnui=True))
    return events.filter(sports_groups__in=host_list)




def get_sorted_events(sort_by, events):
    # Allowed order_by
    allowed_sort_by = ['name', 'description', 'start_date', 'end_date']
    # checks that order_by have a value and that it is in the allowed_order_by
    if sort_by is not None and (sort_by in allowed_sort_by or sort_by[1:] in allowed_sort_by):
        # checks the first character
        type = ''
        if sort_by[0] == '-':
            type = '-'
            sort_by = sort_by[1:]

        # if the sort by is not in the event table we need to find the filed by merging
        if sort_by == 'name':
            sort_by = type + 'eventdescription__name'
        elif sort_by == 'description':
            sort_by = type + 'eventdescription__description_text'

        # return the result
        return events.order_by(sort_by, 'priority', 'start_date')
    else:
        # return the result
        return events.order_by('-priority', 'start_date')




def get_events_json(events):
    """Returnes list of dic of event"""
    return_events = []
    for event in events:
        return_events.append({
            'id': event.id,
            'name': event.name(),
            'place': event.place,
            'description': event.description(),
            'start_date': event.start_date,
            'end_date': event.end_date,
            'priority': event.priority,
            'host': event.get_host(),
            'place': event.place,
            'cover_photo': str(event.cover_photo)
        })
    return return_events
