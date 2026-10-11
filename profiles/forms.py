from django import forms
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


CustomUser = get_user_model()


class UserRegisterForm(UserCreationForm):
    """Form for registering a new user."""

    full_name = forms.CharField(
        required=True,
        label="Full Name",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your full name",
                "class": "mb-3 form-control",
            }
        ),
    )

    email = forms.EmailField(
        required=True,
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "mb-3 form-control",
            }
        ),
    )

    password1 = forms.CharField(
        required=True,
        label="Password",
        strip=False,  # added: don't silently strip spaces
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "mb-3 form-control",
            }
        ),
    )

    password2 = forms.CharField(
        required=True,
        label="Confirm Password",
        strip=False,  # added
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password",
                "class": "mb-3 form-control",
            }
        ),
    )

    class Meta:
        model = CustomUser
        fields = ("email", "full_name", "password1", "password2")

    # added: normalize and reject duplicate emails (case-insensitive)
    def clean_full_name(self):
        full_name = self.cleaned_data["full_name"].strip()
        if not full_name:
            raise forms.ValidationError("Full name cannot be empty.")
        return full_name

    # added: normalize and reject duplicate emails (case-insensitive)
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class UserLoginForm(forms.Form):
    """Form for logging in an existing user."""

    email = forms.EmailField(
        required=True,
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email",
                "class": "mb-3 form-control",
            }
        ),
    )

    password = forms.CharField(
        required=True,
        label="Password",
        strip=False,  # added
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password",
                "class": "mb-3 form-control",
            }
        ),
    )

    remember_me = forms.BooleanField(
        required=False,
        label="Remember me",
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        ),
    )

    # added: normalize so lookups match how emails are stored
    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class ForgotPasswordForm(forms.Form):
    """Form for requesting a password reset."""

    email = forms.EmailField(
        required=True,
        label="Email",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email to reset your password",
                "class": "mb-3 form-control",
            }
        ),
    )

    # added
    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()


class ResetPasswordForm(SetPasswordForm):
    """Form for choosing a new password after following a reset link."""

    new_password1 = forms.CharField(
        label="New password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your new password",
                "class": "mb-3 form-control",
            }
        ),
    )

    new_password2 = forms.CharField(
        label="Confirm new password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your new password",
                "class": "mb-3 form-control",
            }
        ),
    )


class VerifyCodeForm(forms.Form):
    """Form for verifying the registration email code."""

    code = forms.CharField(
        required=True,
        label="Verification Code",
        min_length=6,
        max_length=6,
        validators=[RegexValidator(r"^\d{6}$", "Enter the 6-digit code.")],
        widget=forms.TextInput(
            attrs={
                "placeholder": "000000",
                "class": "mb-3 form-control",
            }
        ),
    )
