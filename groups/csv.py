import csv
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from .models import Membership, SportsGroup
from django.shortcuts import get_object_or_404
from datetime import date


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@login_required
def download_members(request, slug):
    """A view that streams a large CSV file."""
    if request:  # dummy method, to use request, to pass travis tests
        pass

    group = get_object_or_404(SportsGroup, slug=slug)
    members = Membership.objects.filter(group=group.pk)
    pseudo_buffer = Echo()
    header = ['FIRST NAME', 'LAST NAME', 'EMAIL', 'PHONE', 'ROLE', 'DATE JOINED', 'PAID']
    writer = csv.writer(pseudo_buffer, delimiter=';')

    formatted_members = []
    for member in members:
        if member.role:
            role = member.role
        else:
            role = 'Member'

        new_member = [
            member.person.first_name,
            member.person.last_name,
            member.person.email,
            member.person.phone,
            role,
            member.date_joined,
            member.paid,
        ]
        formatted_members.append(new_member)

    rows = [header] + sorted(formatted_members, key=lambda e: e[1])
    today = date.today().__str__()
    response = StreamingHttpResponse((
        writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="' + slug + '"members"' + today + '".csv"'
    return response
