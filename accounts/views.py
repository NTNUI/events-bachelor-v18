from django.shortcuts import render, redirect
from .forms import SignUpForm
from django.contrib.auth import login as auth_login
from django.http import JsonResponse
from django.conf import settings

from .api.exeline import Exeline
from .api.formatter import ApiFormatter
from .api.filterer import ApiFilterer
from .models import User

# not in use
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user,
                       backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def add_users_from_exeline(request):
    def add_or_update_user_to_db(member, nr, total):
        user = None
        customer_no = member['customer_no'] or None
        print('(%i/%i) Updating or creating user with email %s (%s)' %
              (nr, total, member['email'], customer_no))
        obj, created = User.objects.update_or_create(
            customer_no=customer_no,
            defaults={
                'customer_no': member['customer_no'],
                'email': member['email'],
                'first_name': member['first_name'],
                'last_name': member['last_name'],
                'is_active': member['active'],
                'phone': member['mobile'],
                'date_joined': member['registered_date']
            }
        )

    exeline = Exeline(settings.EXELINE_USER, settings.EXELINE_PASSWORD)
    print('Starting!')
    gyms = exeline.get_members_for_all_gyms()
    all_members = gyms['1'] + gyms['2'] + gyms['3']
    print('Got response from API.')
    members = ApiFormatter().format_response_list(all_members)
    ntnui_members = ApiFilterer().filter_only_ntnui_members(members)

    for i, member in enumerate(ntnui_members):
        add_or_update_user_to_db(member, i, len(ntnui_members))

    return JsonResponse({
        'message': 'Skipped users from exeline!',
        'one': len(ntnui_members),
    })
