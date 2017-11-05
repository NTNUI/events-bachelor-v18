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
    if request:  # dummy method, to use request, to pass travis tests

        pass
    formatted_members = []
    max_group_number = 0
    for user in User.objects.all():
        groups = []
        roles = []
        for group_obj in list(Membership.objects.filter(person=user)):
            groups.append(group_obj.group.name)
            roles.append(group_obj.role)

        max_group_number = max(max_group_number, len(list(Membership.objects.filter(person=user))))

        new_member = list()
        new_member.append(user.first_name)
        new_member.append(user.last_name)
        new_member.append(user.email)
        new_member.append(user.phone)
        new_member.append(user.date_joined.date())
        new_member.append(user.is_active)

        for g in groups:
            new_member.append(g)
            r = roles.pop(0)
            if r:
                new_member.append(r)
            else:
                new_member.append("Member")

        formatted_members.append(new_member)
    print(max_group_number)
    pseudo_buffer = Echo()

    header = ['FIRST NAME', 'LAST NAME', 'EMAIL', 'PHONE', 'DATE JOINED', 'ACTIVE']

    for i in range(0, max_group_number):
        header.append('GROUP')
        header.append('ROLE')

    writer = csv.writer(pseudo_buffer, delimiter=';')

    rows = [header]
    for members in formatted_members:
        rows.append(members)

    today = date.today().__str__()
    response = StreamingHttpResponse((
        writer.writerow(row) for row in rows),
        content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="NTNUImembers""' + today + '".csv"'
    return response
