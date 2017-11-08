import csv
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse
from .models import Membership, SportsGroup
from accounts.models import Contract
from django.shortcuts import get_object_or_404
from datetime import date, datetime

YEAR_MEMBERSHIP = 10
HALF_YEAR_MEMBERSHIP = 20


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
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    # rows = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    if request:
        pass

    group = get_object_or_404(SportsGroup, slug=slug)
    members = Membership.objects.filter(group=group.pk)
    header = ['FIRST NAME', 'SECOND NAME', 'EMAIL', 'PHONE', 'PAID']

    formatted_members = []
    for member in members:
        new_member = [
            member.person.first_name,
            member.person.last_name,
            member.person.email,
            member.person.phone,
            member.paid,
        ]
        formatted_members.append(new_member)

    sorted_formatted_members = sorted(formatted_members, key=lambda e: e[1])
    rows = [header] + sorted_formatted_members
    today = date.today().__str__()

    response = list_to_csv_http_response(rows)
    response['Content-Disposition'] = 'attachment; filename=""' + slug + '"members""' + today + '".csv"'
    return response

def download_yearly_group_members_2017(request, slug):
    return download_yearly_group_members(request, slug, 2017)

def download_yearly_group_members_2018(request, slug):
    return download_yearly_group_members(request, slug, 2018)

def download_yearly_group_members_2019(request, slug):
    return download_yearly_group_members(request, slug, 2019)

def download_yearly_group_members_2020(request, slug):
    return download_yearly_group_members(request, slug, 2020)

@login_required
def download_yearly_group_members(request, slug, year):

    if request:
        pass

    group = get_object_or_404(SportsGroup, slug=slug)

    start_date = date(year, 8, 1)
    end_date = date(year+1, 1, 31)

    contracts = Contract.objects.filter(
        person__membership__group=group.pk,
        expiry_date__year=year+1,
        expiry_date__month=8,
        contract_type=YEAR_MEMBERSHIP) | Contract.objects.filter(
            person__membership__group=group.pk,
            expiry_date__range=(start_date, end_date)
            )

    formatted_members = []
    header = ['FIRST NAME', 'SECOND NAME', 'EMAIL', 'PHONE', 'EXP DATE',
        'CONTRACT TYPE']

    for contract in contracts:
        formatted_members.append([
            contract.person.first_name,
            contract.person.last_name,
            contract.person.email,
            contract.person.phone,
            contract.expiry_date,
            contract.contract_type
            ])

    sorted_formatted_members = sorted(formatted_members, key=lambda e: e[1])

    for i in range(1, len(sorted_formatted_members)):
        if sorted_formatted_members[i][2] == sorted_formatted_members[i-1][2]:
            sorted_formatted_members.remove(sorted_formatted_members[i])

    rows = [header] + sorted_formatted_members
    response = list_to_csv_http_response(rows)
    response['Content-Disposition'] = 'attachment; filename=""' + slug + '"members""' + str(year) + '".csv"'
    return response




def list_to_csv_http_response(inputList):
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer, delimiter=';')
    response = StreamingHttpResponse((
        writer.writerow(row) for row in inputList), content_type="text/csv")
    return response
