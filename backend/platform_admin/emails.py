"""Platform admin notification emails."""
import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _login_url() -> str:
    return f"{settings.FRONTEND_URL.rstrip('/')}/login"


def send_admin_assignment_email(
    *,
    user,
    estate,
    role_name: str,
    assigned_by,
    is_new_user: bool,
    temporary_password: str | None = None,
) -> bool:
    """Send invite email when an estate admin role is assigned. Returns True if sent."""
    login_url = _login_url()
    estate_name = estate.name
    assigned_by_name = assigned_by.get_full_name() or assigned_by.email

    if is_new_user and temporary_password:
        subject = f"You've been invited as {role_name} for {estate_name}"
        message = (
            f"Hello {user.first_name or user.email},\n\n"
            f"{assigned_by_name} assigned you as {role_name} for {estate_name} on EstateOS.\n\n"
            f"Sign in with:\n"
            f"  Email: {user.email}\n"
            f"  Temporary password: {temporary_password}\n\n"
            f"Login: {login_url}\n\n"
            f"Change your password after your first login.\n"
        )
    else:
        subject = f"New {role_name} access for {estate_name}"
        message = (
            f"Hello {user.first_name or user.email},\n\n"
            f"{assigned_by_name} assigned you as {role_name} for {estate_name} on EstateOS.\n\n"
            f"Sign in with your existing account: {login_url}\n"
        )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception(
            "Failed to send admin assignment email to %s for estate %s",
            user.email,
            estate.id,
        )
        return False
