import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import yaml
from datetime import date
with open("config.yml", 'r') as configInfo:
    config = yaml.safe_load(configInfo)

port = config['Mail']['port']
password = config['Mail']['pw']
user = config['Mail']['user']
outgoing = config['Mail']['outgoing']
sender = config['Mail']['sender']
receiver = config['Mail']['receiver']
message = """\
Subject: Hi there

This message is sent from Python."""

# Post Contacts Audit Info
post_audit_subject = config['PostAudit']['subject']
post_audit_body = config['PostAudit']['body']
post_audit_message = MIMEMultipart()
post_audit_message["From"] = sender
post_audit_message["To"] = receiver
post_audit_message["Subject"] = post_audit_subject
post_audit_message["Bcc"] = receiver # Recommended for mass emails
post_audit_message.attach(MIMEText(post_audit_body, "plain"))
post_audit_file = "Audits\Post\ConstantContact_API_Add_" + str(date.today()) + '.xlsx'


with open(post_audit_file, "rb") as attachment:
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

encoders.encode_base64(part)

part.add_header(
    "Content-Disposition",
    f"attachment; filename= {post_audit_file}",
)

post_audit_message.attach(part)
text = post_audit_message.as_string()

# Basic SSL Email


def email_post_audit_attachment():
    print('emailing new contact post audit attachment to group: ' + receiver)
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(outgoing, port, context=context) as server:
        server.login(user, password)
        server.sendmail(sender, receiver, text)