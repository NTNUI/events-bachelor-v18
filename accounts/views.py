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
    def add_or_update_user_to_db(member):
        user = None
        email = member['email'] or None
        print('Saving user with email %s' % email)
        if email is None:
            return
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email)
        except accounts.models.DoesNotExist:
            user = User.objects.create(email=email)

        user.first_name = member['first_name']
        user.last_name = member['last_name']
        user.is_active = member['active']
        user.phone = member['mobile']
        #user.date_joined = member['registered_date']
        user.save()

    exeline = Exeline(settings.EXELINE_USER, settings.EXELINE_PASSWORD)
    print('Starting!')
    gyms = exeline.get_members_for_all_gyms()
    all_members = gyms['1'] + gyms['2'] + gyms['3']
    print('Got response from API.')
    #all_members = exeline.get_members_for_gym('3')
    members = ApiFormatter().format_response_list(all_members)
    ntnui_members = ApiFilterer().filter_only_ntnui_members(members)

    for member in ntnui_members:
        add_or_update_user_to_db(member)

    return JsonResponse({
        'message': 'Skipped users from exeline!',
        'one': len(ntnui_members),
    })
