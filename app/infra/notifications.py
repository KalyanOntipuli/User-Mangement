from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

from fastapi import HTTPException
from app.infra.email_templates import get_credentials_sending_template
from app.utilities.constants import SMTP_EMAIL, SMTP_PASSWORD
from starlette import status


async def send_notification(email: str, subject: str, html_content: str):
    sender_email = SMTP_EMAIL
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = sender_email
    smtp_password = SMTP_PASSWORD
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject
    part = MIMEText(html_content, "html")
    message.attach(part)

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, message.as_string())

    except smtplib.SMTPException as e:
        raise


async def notification_for_agent_to_send_credentials(
    employee_name: str, company_name: str, email: str, password: str
):
    try:
        notify_info1 = (
            f"Welcome to Markwave AI, We are excited to have you join our team. "
            f"As an Agent of Markwave, you can now access our platform to manage your "
            f"payslips and stay connected with the team."
        )

        notify_info2 = (
            "Please make sure to log in to the platform at your earliest convenience and update your password "
            "for security reasons. If you have any questions or need assistance, feel free to contact our support team. "
            "We're here to help!"
        )

        html_content = get_credentials_sending_template(
            employee_name, notify_info1, notify_info2, email, password
        )

        subject = "Welcome to Markwave AI! Your Login Credentials"

        await send_notification(email, subject, html_content)

    except Exception as error:
        raise HTTPException(
            detail=str(error), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
