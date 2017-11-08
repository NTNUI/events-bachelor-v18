from django.shortcuts import redirect
from groups.models import SportsGroup, Board
from hs.models import MainBoard


def is_member(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            if request.user not in SportsGroup.objects.get(slug=kwargs['slug']):
                return redirect('group_index', slug=kwargs['slug'])
        except SportsGroup.DoesNotExist:
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def is_board(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            if request.user not in SportsGroup.objects.get(slug=kwargs['slug']).active_board:
                return redirect('group_index', slug=kwargs['slug'])
        except Board.DoesNotExist:
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def is_main_board(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            if request.user not in MainBoard.objects.all().get():
                return redirect('list_groups')
        except MainBoard.DoesNotExist:
            pass

        return view_func(request, *args, **kwargs)
    return _wrapped_view_func
