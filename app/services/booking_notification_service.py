import logging
import smtplib
from email.message import EmailMessage

import httpx

from app.core.config import settings
from app.models.booking import Booking


logger = logging.getLogger(__name__)


class BookingNotificationService:
    def send_status_update(self, booking: Booking) -> dict[str, dict[str, bool | str]]:
        return {
            "email": self._send_email(booking),
            "sms": self._send_sms(booking),
        }

    def _send_email(self, booking: Booking) -> dict[str, bool | str]:
        if not booking.customer_email:
            return {"sent": False, "error": "No customer email address is available."}

        if not settings.SMTP_HOST or not settings.EMAIL_FROM:
            return {"sent": False, "error": "SMTP email settings are incomplete."}

        if bool(settings.SMTP_USERNAME) != bool(settings.SMTP_PASSWORD):
            return {"sent": False, "error": "Configure both SMTP username and password, or neither."}

        customer_name = booking.customer_name or "Customer"
        status_text = booking.status.replace("_", " ").capitalize()
        message = EmailMessage()
        message["Subject"] = f"Your Conniecomes appointment is {status_text.lower()}"
        message["From"] = settings.EMAIL_FROM
        message["To"] = booking.customer_email
        message.set_content(
            f"Hello {customer_name},\n\n"
            f"Your appointment status has been updated to: {status_text}.\n\n"
            f"Service: {booking.service}\n"
            f"Date: {booking.booking_date}\n"
            f"Time: {booking.booking_time.strftime('%H:%M')}\n\n"
            "Please contact Conniecomes Beauty Salon if you have any questions."
        )

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20) as server:
                if settings.SMTP_USE_TLS:
                    server.starttls()
                if settings.SMTP_USERNAME:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                server.send_message(message)
        except (OSError, smtplib.SMTPException):
            logger.exception("Failed to send booking status email for booking %s", booking.id)
            return {"sent": False, "error": "Email delivery failed. Check the SMTP settings and server logs."}

        return {"sent": True}

    def _send_sms(self, booking: Booking) -> dict[str, bool | str]:
        if not booking.customer_phone:
            return {"sent": False, "error": "No customer phone number is available."}

        if not all((
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_FROM_NUMBER,
        )):
            return {"sent": False, "error": "Twilio SMS settings are incomplete."}

        status_text = booking.status.replace("_", " ").capitalize()
        body = (
            f"Conniecomes: your {booking.service} appointment on "
            f"{booking.booking_date} at {booking.booking_time.strftime('%H:%M')} "
            f"is now {status_text.lower()}."
        )
        url = (
            "https://api.twilio.com/2010-04-01/Accounts/"
            f"{settings.TWILIO_ACCOUNT_SID}/Messages.json"
        )

        try:
            response = httpx.post(
                url,
                auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                data={
                    "From": settings.TWILIO_FROM_NUMBER,
                    "To": booking.customer_phone,
                    "Body": body,
                },
                timeout=20,
            )
            response.raise_for_status()
        except httpx.HTTPError:
            logger.exception("Failed to send booking status SMS for booking %s", booking.id)
            return {"sent": False, "error": "SMS delivery failed. Check the Twilio settings and server logs."}

        return {"sent": True}
