import os
import ssl
import certifi
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jinja2 import Environment, FileSystemLoader,select_autoescape
import aiosmtplib

load_dotenv()
print(certifi.where())

print(ssl.get_default_verify_paths().cafile)


class Envs:
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")
    MAIL_STARTTLS = os.getenv("MAIL_STARTTLS", "True").lower() in ["true", "1", "yes"]
    MAIL_SSL_TLS = os.getenv("MAIL_SSL_TLS", "False").lower() in ["true", "1", "yes"]
    
config = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=Envs.MAIL_STARTTLS,
    MAIL_SSL_TLS=Envs.MAIL_SSL_TLS, 
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER="api/templates"
)

env = Environment(
    loader=FileSystemLoader(config.TEMPLATE_FOLDER),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_registration_mail(subject: str, email_to: str, body: dict):
    template = env.get_template("email.html")
    html_content = template.render(body)
    
    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html_content,
        subtype="html"
    )
    
    context = ssl.create_default_context(cafile='/private/etc/ssl')
    
    async with aiosmtplib.SMTP(
        hostname=config.MAIL_SERVER,
        port=config.MAIL_PORT,
        use_tls=config.MAIL_SSL_TLS,
        start_tls=config.MAIL_STARTTLS,
        tls_context=context
    ) as smtp:
        await smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
        await smtp.send_message(message)