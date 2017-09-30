from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import SportsGroup, Membership

@login_required
def members(request, slug):
    group = {
        'name': 'NTNUI Volleyball',
        'members': [
            {
                'name': 'Todd Packer',
                'phone': '93827492',
                'email': 'todd.packer@online.com',
                'paid': False,
            },
            {
                'name': 'James Halpert',
                'phone': '23092340',
                'email': 'jameshalpert@gmail.com',
                'paid': True,
            },
            {
                'name': 'Angela Frankenstein',
                'phone': '21093801',
                'email': 'frankela@steinberg.org',
                'paid': True,
            },
            {
                'name': 'Michael Scott',
                'phone': '99883212',
                'email': 'michael.scott@dundermifflin.com',
                'paid': False,
            },
            {
                'name': 'Creed Bratton',
                'phone': '49289201',
                'email': 'mynameiscreed@bratton.com',
                'paid': False,
            },
            {
                'name': 'Phyllis Vance',
                'phone': '99883212',
                'email': 'phyllis@vancerefrigiration.com',
                'paid': True,
            },
            {
                'name': 'Stanley Hudson',
                'phone': '49209281',
                'email': 'stanley.hudson@dundermifflin.com',
                'paid': True,
            },
            {
                'name': 'Dwight K. Schrute',
                'phone': '49209281',
                'email': 'dwight.k.schrute@schrutefarms.net',
                'paid': True,
            },
            {
                'name': 'Toby Flenderson',
                'phone': '93282311',
                'email': 'toby.flenderson@dundermifflin.com',
                'paid': True,
            },
            {
                'name': 'Pam Beesly',
                'phone': '44920082',
                'email': 'beeslyarts@gmail.com',
                'paid': False,
            },
            {
                'name': 'Ryan Howard',
                'phone': '94827328',
                'email': 'ryan.the.fireguy@hotmail.com',
                'paid': False,
            },
            {
                'name': 'Andrew Bernard',
                'phone': '49209281',
                'email': 'andrew.bernard@cornell.edu',
                'paid': True,
            },
            {
                'name': 'Robert California',
                'phone': '99382392',
                'email': 'givemeonemillion@robertcalifornia.com',
                'paid': False,
            },
            {
                'name': 'Jan Levinson',
                'phone': '11839238',
                'email': 'jan.levinson@dundermifflin.com',
                'paid': True,
            },
            {
                'name': 'Roy Anderson',
                'phone': '88292038',
                'email': 'thebestroy@aol.com',
                'paid': False,
            },
        ]
    }
    print(slug)
    groups = SportsGroup.objects.filter(slug='ntnui')
    if (len(groups) != 1):
        raise Http404("Group does not exist")
    group = groups[0]
    members = Membership.objects.filter(group=group.pk)
    return render(request, 'groups/members.html', { 'group': group, 'members': members })


def list_groups(request):
    return render(request, 'groups/list_groups.html')
