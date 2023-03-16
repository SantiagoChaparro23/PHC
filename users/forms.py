from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User




def validate_school_email(value):
    print(value)
    
    user = User.objects.filter(username__contains=value.lower()).first()
    print(user)
    if user:
        raise ValidationError("Ya existe el usuario")
    else:
        return value



class LoginForm(forms.Form):
    #email = forms.CharField()
    email = forms.CharField(validators=[RegexValidator(
            regex='^^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$',
            message='Ingrese un email valido',
            code='invalid_email'
        )],)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput())




