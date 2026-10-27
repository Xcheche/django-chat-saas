from datetime import timedelta
from importlib import import_module

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from profiles.models import Profiles, ResetLink


pytestmark = pytest.mark.django_db
User = get_user_model()


@pytest.fixture
def user():
    return User.objects.create_user(
        email="user@example.com",
        full_name="Test User",
        password="StrongPass123!",
    )


# ==================== Login ====================
def test_login_success(client, user, monkeypatch):
    monkeypatch.setattr("profiles.views.login.send_login_success_email", lambda **kwargs: None)

    response = client.post(reverse("profiles:login"), {
        "email": user.email,
        "password": "StrongPass123!",
    })

    assert response.status_code == 302
    assert response.url == reverse("profiles:home")


def test_login_wrong_password_increments_attempts(client, user, monkeypatch):
    monkeypatch.setattr("profiles.views.login.send_login_success_email", lambda **kwargs: None)

    client.post(reverse("profiles:login"), {
        "email": user.email,
        "password": "wrong-password",
    })

    user.refresh_from_db()
    assert user.failed_login_attempts == 1


# ================= Code Verification =================
def test_code_verification_creates_user(client, monkeypatch):
    view_module = import_module("profiles.views.code_verification")
    monkeypatch.setattr(view_module, "send_login_success_email", lambda **kwargs: None)
    session = client.session
    session.update({
        "email": "new@example.com",
        "full_name": "New User",
        "password": "StrongPass123!",
        "register_code": "123456",
    })
    session.save()

    response = client.post(reverse("profiles:code_verification"), {"code": "123456"})

    assert response.status_code == 302
    assert response.url == reverse("profiles:home")
    assert User.objects.filter(email="new@example.com").exists()


def test_code_verification_wrong_code(client):
    session = client.session
    session["register_code"] = "123456"
    session.save()

    response = client.post(reverse("profiles:code_verification"), {"code": "000000"})

    assert response.status_code == 200
    assert client.session["code_tries"] == 1


# ==================== Resend Code ====================
def test_resend_code_sends_new_code(client, monkeypatch):
    sent = []
    view_module = import_module("profiles.views.resend_code")
    monkeypatch.setattr(
        view_module,
        "send_new_verification_code_email",
        lambda email, code: sent.append((email, code)),
    )
    session = client.session
    session["email"] = "user@example.com"
    session["resend_available_at"] = 0
    session.save()

    response = client.get(reverse("profiles:resend_code"))

    assert response.status_code == 302
    assert sent[0][0] == "user@example.com"
    assert len(sent[0][1]) == 6


# ================== Forgot Password ==================
def test_forgot_password_creates_reset_link(client, user, monkeypatch):
    view_module = import_module("profiles.views.forgot_password")
    monkeypatch.setattr(view_module, "send_password_reset_email", lambda **kwargs: None)

    response = client.post(reverse("profiles:forgot_password"), {"email": user.email})

    assert response.status_code == 302
    assert ResetLink.objects.filter(user=user, used_at__isnull=True).exists()


# =================== Reset Password ===================
def test_reset_password_changes_password(client, user):
    reset_link = ResetLink.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(minutes=10),
    )

    response = client.post(
        reverse("profiles:reset_password", kwargs={"unique_id": reset_link.uniqueId}),
        {
            "new_password1": "NewStrongPass123!",
            "new_password2": "NewStrongPass123!",
        },
    )

    assert response.status_code == 302
    assert response.url == reverse("profiles:login")
    user.refresh_from_db()
    assert user.check_password("NewStrongPass123!")


# ======================== Logout ========================
def test_logout_redirects_authenticated_user(client, user):
    client.force_login(user)

    response = client.get(reverse("profiles:logout"))

    assert response.status_code == 302
    assert response.url == reverse("profiles:login")


# ====================== Registration ======================
def test_register_get_renders_empty_form(client):
    response = client.get(reverse("profiles:register"))

    assert response.status_code == 200
    assert "profiles/register.html" in [template.name for template in response.templates]
    assert "form" in response.context


def test_register_valid_post_sends_code(client, valid_data, sent_codes):
    response = client.post(reverse("profiles:register"), valid_data)

    assert response.status_code == 302
    assert response.url == reverse("profiles:code_verification")
    assert sent_codes == [(valid_data["email"], client.session["register_code"])]


def test_register_invalid_post_does_not_send_code(client, valid_data, sent_codes):
    response = client.post(
        reverse("profiles:register"),
        {**valid_data, "password2": "does-not-match"},
    )

    assert response.status_code == 200
    assert response.context["form"].errors
    assert sent_codes == []


def test_register_logged_in_user_is_redirected(client, user):
    client.force_login(user)

    response = client.get(reverse("profiles:register"))

    assert response.status_code == 302


# ======================= Profile Signal =======================
def test_new_user_creates_profile(user):
    assert Profiles.objects.filter(user=user).exists()


# ====================== Staff Admin Access =====================
def test_staff_user_can_access_admin(client, user):
    user.is_staff = True
    user.save(update_fields=["is_staff"])
    client.force_login(user)

    response = client.get(reverse("admin:index"))

    assert response.status_code == 200
