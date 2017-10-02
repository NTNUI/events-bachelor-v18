from ntnui.models import User
from django.contrib.auth.forms import UserCreationForm

class SignUpForm(UserCreationForm):
    """
    A form that creates a user, with no privileges, from the given email and
    password.
    """

    def __init__(self, *args, **kargs):
        super(SignUpForm, self).__init__(*args, **kargs)
        self.fields.pop('username', None)

    class Meta:
        model = User
        fields = ("email",)
