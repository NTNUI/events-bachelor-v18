from django import forms
from .models import MainBoard


class SettingsForm(forms.Form):
    cover_photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.slug = kwargs.pop('slug') if 'slug' in kwargs else ''
        super(SettingsForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super(SettingsForm, self).clean()
        self.validate_board()

    def get_board(self):
        try:
            return MainBoard.objects.get(slug=self.slug)
        except MainBoard.DoesNotExist:
            return None

    def validate_board(self):
        try:
            return MainBoard.objects.get(slug=self.slug)
        except MainBoard.DoesNotExist:
            self.add_error(None, "Invalid board")

    def set_images(self):
        board = self.get_board()
        cover_photo = self.cleaned_data.get('cover_photo')
        if cover_photo:
            board.cover_photo = cover_photo
        board.save()
