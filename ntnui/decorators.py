from django.shortcuts import redirect
from groups.models import SportsGroup


def is_member(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            if request.user not in SportsGroup.objects.get(slug=kwargs['slug']):
                return redirect('group_index', slug=kwargs['slug'])
        except:
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


def is_board(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            if request.user not in SportsGroup.objects.get(slug=kwargs['slug']).active_board:
                return redirect('group_index', slug=kwargs['slug'])
        except:
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
