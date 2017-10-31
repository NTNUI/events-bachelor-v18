import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import StreamingHttpResponse


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
    rows = (["Row {}".format(idx), str(idx)] for idx in range(10))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((
        writer.writerow(['field1', 'field2', 'field3', 'field4']) for row in rows),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename=""' + slug + '"members.csv"'
    return response
