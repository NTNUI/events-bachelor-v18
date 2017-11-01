import csv
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from .models import Membership, SportsGroup
from django.shortcuts import get_object_or_404

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

@login_required
def download_all_members(request,slug):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    # rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    group = get_object_or_404(SportsGroup, slug=slug)
    members = Membership.objects.filter(group=group.pk)
    pseudo_buffer = Echo()
    header = ['NAME', 'EMAIL', 'PHONE']
    writer = csv.writer(pseudo_buffer, delimiter=';')

    formatted_members = []
    for member in members:
        new_member = [
            member.person.first_name + " " + member.person.last_name,
            member.person.email,
            member.person.phone,
        ]
        formatted_members.append(new_member)


    rows = [header] + formatted_members
    response = StreamingHttpResponse((
        writer.writerow(row) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=""' + slug + '"members.csv"'
    return response
