from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import widgets

CustomUser = get_user_model()


class UserRegisterForm(UserCreationForm):
    """
    Form for registering a new user. Inherits from Django's built-in UserCreationForm.
    """

    class Meta:
        model = get_user_model()  # Use the custom user model
        fields = (
            "email",
            "password1",
            "password2",
        )  # Fields to include in the mb-3 form

        email = forms.EmailField(
            required=True,
            label="Email",
            widget=forms.EmailInput(
                attrs={"class": "mb-3 form-control", "placeholder": "Enter your email"}
            ),
        )
        password1 = forms.CharField(
            required=True,
            label="Password",
            widget=forms.PasswordInput(
                attrs={
                    "class": "mb-3 form-control",
                    "placeholder": "Enter your password",
                }
            ),
        )
        password2 = forms.CharField(
            required=True,
            label="Confirm Password",
            widget=forms.PasswordInput(
                attrs={
                    "class": "mb-3 form-control",
                    "placeholder": "Confirm your password",
                }
            ),
        )


class UserLoginForm(forms.Form):
    """
    Form for logging in an existing user.
    """

    email = forms.CharField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "mb-3 form-control", "placeholder": "Enter your email"}
        ),
    )
    password = forms.CharField(
        required=True,
        label="Password",
        widget=forms.PasswordInput(
            attrs={"class": "mb-3 form-control", "placeholder": "Enter your password"}
        ),
    )


class ForgotPasswordForm(forms.Form):
    """
    Form for requesting a password reset.
    """

    email = forms.CharField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "mb-3 form-control", "placeholder": "Enter your email"}
        ),
    )


class VerifyCodeForm(forms.Form):
    """
    Form for verifying a code sent to the user's email.
    """

    code = forms.CharField(
        required=True,
        label="Verification Code",
        widget=forms.NumberInput(
            attrs={"class": "mb-3 form-control", "placeholder": "00000000"}
        ),
    )
