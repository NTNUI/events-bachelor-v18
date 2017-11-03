import csv
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from groups.models import Membership, SportsGroup
from accounts.models import User
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
def download_all_members(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    # rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    if request:
        pass
    user_groups = {}
    for user in User.objects.all():
        user_groups[user] = list(Membership.objects.filter(person=user))

    
    print(user_groups)

    groups = SportsGroup.objects.all().order_by('name')
    all_members = []
    for group in groups:
        group_members = Membership.objects.filter(group=group.pk)
        formatted_group_members = []
        for member in group_members:
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
                group,
            ]
            formatted_group_members.append(new_member)
            sorted_formatted_group_members = sorted(formatted_group_members, key=lambda e: e[1])

        all_members.append(sorted_formatted_group_members)
    pseudo_buffer = Echo()
    header = ['FIRST NAME', 'LAST NAME', 'EMAIL', 'PHONE', 'ROLE', 'DATE JOINED', 'PAID', 'GROUP']
    writer = csv.writer(pseudo_buffer, delimiter=';')

    rows = [header]
    for group_members in all_members:
        rows = rows + group_members

    today = date.today().__str__()
    response = StreamingHttpResponse((
        writer.writerow(row) for row in rows),
        content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="NTNUImembers""' + today + '".csv"'
    return response
