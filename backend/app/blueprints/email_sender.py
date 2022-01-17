import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.utils import formataddr
from pathlib import Path
from string import Template

sender_email = os.environ.get('EMAIL_NAME', "ofisino@gmail.com")
sender_name = "Ofisino"
password = os.environ.get('EMAIL_PASSWORD')

PARENT = Path(__file__).absolute().parent
EMAIL_BOX_MODIFICATIONS = PARENT / 'email_box_modifications.html'
EMAIL_MEETING_ROOM_MODIFICATIONS = PARENT / 'email_meeting_room_modifications.html'


def create_box_email_format(box, older_name, older_description):
    new_data = ""
    if box.name != older_name:
        new_data = add_new_data(older_name, box.name, "Nombre", new_data)
    if box.description != older_description:
        new_data = add_new_data(older_description, box.description, "Descripcion", new_data)

    with EMAIL_BOX_MODIFICATIONS.open('r') as f:
        email_box_body = Template(f.read()).safe_substitute(newdata=new_data, boxname=box.name)
    return email_box_body


def create_meeting_room_email_format(meeting_room, older_meeting_room):
    new_data = ""
    if meeting_room.name != older_meeting_room.name:
        new_data = add_new_data(older_meeting_room.description, meeting_room.description, "Nombre", new_data)

    if meeting_room.capacity != older_meeting_room.capacity:
        new_data = add_new_data(older_meeting_room.capacity, meeting_room.capacity, "Capacidad", new_data)

    if meeting_room.features != older_meeting_room.features:
        new_data = f"{new_data}{_parser_features(meeting_room.features, older_meeting_room.features)}"

    if meeting_room.description != older_meeting_room.description:
        new_data = add_new_data(older_meeting_room.description, meeting_room.description, "Descripcion", new_data)

    with EMAIL_MEETING_ROOM_MODIFICATIONS.open('r') as f:
        email_meeting_room_body = Template(f.read()).safe_substitute(newdata=new_data, saladereunion=meeting_room.name)
    return email_meeting_room_body


def add_new_data(before, after, feature, new_data):
    if before is not None and after is not None:
        return (f'{new_data}<li>{feature.capitalize()}: <span style="text-decoration:line-through;"> '
                f'{before}</span>  {after}</li> ')
    elif before:
        return (f'{new_data}<li>{feature.capitalize()}: <span style="text-decoration:line-through;"> '
                f'{before}</span></li> ')
    else:
        return f'{new_data}<li>{feature.capitalize()}: {after}</li> '


def _parser_features(new_features, old_features):
    new_data = f"<li>Caracteristicas: <br>"
    for key, value in new_features.items():
        the_key = key.replace("_", " ").capitalize()
        if value != old_features[key]:
            new_data = (f'{new_data}{the_key}: <span style="text-decoration:line-through;">'
                        f'{old_features[key]}</span>  {value}<br>')
        else:
            new_data = f"{new_data}{the_key}: {value}<br>"

    return f'{new_data}</li>'


def send_email(email, name, subject, body):
    msg = MIMEText(body, 'html')
    msg['To'] = formataddr((name, email))
    msg['From'] = formataddr((sender_name, sender_email))
    msg['Subject'] = subject
    server = smtplib.SMTP('smtp.gmail.com', 587)
    try:
        context = ssl.create_default_context()
        server.starttls(context=context)
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        print('Email sent')
    except Exception as e:
        print(f'Oh no, algo malo paso {e}')
    finally:
        print('Cerrando server')
        server.quit()
