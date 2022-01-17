# -*- coding: utf-8 -*-
import os
from pprint import pprint

import click
import requests

from app.api import create_app
from app.api_config import get_config
from app.api_credentials import get_service_credentials_or_abort_with_http_500
from app.blueprints.api_extra_functions import create_calendar
from app.blueprints.helpers import get_model_by_email, get_model_by_id
from app.calendar_class import CalendarManager
from app.persistence import models as m
from app.persistence.basemodel import BaseModel
from app.persistence.session import get_engine, get_session


@click.group()
def db():
    """DB Command group"""


@db.command()
def listusers():
    app = create_app()
    with app.app_context():
        s = get_session()
        users = s.query(m.User.name, m.User.email, m.User.admin).all()
        pprint(users)


@db.command()
@click.argument('name')
@click.argument('email')
@click.option('--admin', is_flag=True, default=False)
def adduser(name, email, admin=False):
    app = create_app()
    with app.app_context():
        s = get_session()
        previous_user = s.query(m.User).filter_by(email=email).first()
        if previous_user:
            print(f"❌ A user ({previous_user.name}) already exists with email={email!r}")
            return

        user = m.User(name=name, email=email, admin=bool(admin))
        s.add(user)
        s.commit()
        print(f"✨ {user.name} was created with email {user.email}. Admin={user.admin}")


@db.command()
@click.argument('email')
def admin(email):
    app = create_app()
    with app.app_context():
        s = get_session()
        user_from_db = get_model_by_email(email)
        if user_from_db:
            user_from_db.admin = not user_from_db.admin
            s.commit()
            print(f"✨ User {user_from_db.name} changed. Admin={user_from_db.admin}")


@db.command()
def create():
    config = get_config()
    engine = get_engine(config.DATABASE_URL)

    app = create_app()
    with app.app_context():
        BaseModel.metadata.create_all(engine)

    print("✨  All models were created")


@db.command()
def recreate():
    config = get_config()
    engine = get_engine(config.DATABASE_URL)

    app = create_app()
    with app.app_context():
        _delete_meetings_and_reservations()
        print("Dropping all tables")
        BaseModel.metadata.drop_all(engine)
        print("Creating all tables")
        BaseModel.metadata.create_all(engine)

    print("✨  All models were created from scratch")


@db.command()
def populate():
    print("Creating app")
    app = create_app()

    print("Generating app context")
    with app.app_context():
        print("🪄  Creating organization with building")
        # Create organization
        monsters_inc = m.Organization(name='Ofisino ORG', description='Organización Ofisino')

        # Create building 1
        building = m.Building(
            name='Sede Central',
            location='CABA',
            description='Edificio principal Ofisino ORG',
        )
        monsters_inc.building.append(building)

        print("🪄  Adding workspaces with boxes")
        # Create working spaces with boxes and append to building 1
        planta_baja_ws = m.WorkingSpace(name='Sector IT', area=30, square_meters_per_box=9,
                                        description='Servidores, Desarrollo y Soporte Técnico')
        planta_alta_ws = m.WorkingSpace(name='Sector Administración', area=50, square_meters_per_box=4,
                                        description='Finanzas, RRHH y Ventas')
        planta_baja_ws.box = [m.Box(name=f'Box {x + 1} (IT)', description='') for x in range(3)]
        planta_alta_ws.box = [m.Box(name=f'Box {x + 1} (ADMIN)', description='') for x in range(5)]
        building.working_space.append(planta_baja_ws)
        building.working_space.append(planta_alta_ws)

        print("🪄  Adding secondary building")
        # Create building 2
        building_2 = m.Building(
            name='Anexo Ejecutivo',
            location='Microcentro',
            description='Edificio Gerencia',
        )
        monsters_inc.building.append(building_2)

        print("🪄  Adding workspaces with boxes")
        # Create working spaces with boxes and append to building 2
        working_space_1 = m.WorkingSpace(name='Sector Gerencial', area=60, square_meters_per_box=12,
                                         description='CEOS y Gerentes')
        working_space_1.box = [m.Box(name=f'Box {x + 1} (GER)', description='') for x in range(5)]
        building_2.working_space.append(working_space_1)

        print("🪄  Creating calendar for blue room")
        calendar_id_1 = create_calendar(calendar_summary="Sala Azul")
        features_mr1 = {
            'aire_acondicionado': 1,
            'computadoras': 0,
            'mesas': 1,
            'proyector': 0,
            'sillas': 4,
            'ventanas': 2
        }
        meeting_room_1 = m.MeetingRoom(name="Sala Azul",
                                       capacity=4,
                                       features=features_mr1,
                                       calendar=calendar_id_1,
                                       description='')
        building.meeting_room.append(meeting_room_1)

        print("🪄  Creating calendar for green room")
        calendar_id_2 = create_calendar(calendar_summary="Sala Verde")
        features_mr2 = {
            'aire_acondicionado': 1,
            'computadoras': 1,
            'mesas': 1,
            'proyector': 1,
            'sillas': 5,
            'ventanas': 1
        }
        meeting_room_2 = m.MeetingRoom(name="Sala Verde",
                                       capacity=5,
                                       features=features_mr2,
                                       calendar=calendar_id_2,
                                       description='')
        building.meeting_room.append(meeting_room_2)

        print("🪄  Creating calendar for orange room")
        calendar_id_3 = create_calendar(calendar_summary="Sala Naranja")
        features_mr3 = {
            'aire_acondicionado': 1,
            'computadoras': 10,
            'mesas': 2,
            'proyector': 1,
            'sillas': 10,
            'ventanas': 2
        }
        meeting_room_3 = m.MeetingRoom(name="Sala Naranja",
                                       capacity=10,
                                       features=features_mr3,
                                       calendar=calendar_id_3,
                                       description='')
        building_2.meeting_room.append(meeting_room_3)

        print("🪄  Adding all entities to database")
        s = get_session()
        s.add(monsters_inc)
        s.commit()
        print("✨  An organization was created with buildings that has working spaces and meeting rooms.")
        ######################################################################################################
        # Add Users and a default Admin to fast test with commands
        ######################################################################################################
        service_credentials = get_service_credentials_or_abort_with_http_500()
        cman = CalendarManager(config=service_credentials)
        users = cman.get_users()
        users_to_db = [
            m.User(email=user['primaryEmail'], name=user['name']['fullName'], admin=True)
            if user['primaryEmail'].startswith('nis@')
            else m.User(email=user['primaryEmail'], name=user['name']['fullName'])
            for user in users
        ]
        users_to_db.append(m.User(name='ADMIN', email='ADMIN@ADMIN.com', admin=True))
        s = get_session()
        s.add_all(users_to_db)
        s.commit()
        print(f"✨ All users {[x.name for x in users_to_db]} added to DB")
        ######################################################################################################
        # ~MEETINGS~ #
        ######################################################################################################
        print("🔨  Trying to generate the meetings")
        generatemeetings()
        ######################################################################################################
        # ~RESERVATIONS~ #
        ######################################################################################################
        print("🔨  Trying to make the reservations")
        makereservations()


@db.command()
def clear():
    app = create_app()
    with app.app_context():
        _delete_meetings_and_reservations()


@db.command()
def drop():
    config = get_config()
    engine = get_engine(config.DATABASE_URL)
    app = create_app()
    with app.app_context():
        _delete_meetings_and_reservations()
        BaseModel.metadata.drop_all(engine)
        print("🧹  All tables were dropped")


def deletemeetings():
    app = create_app()
    with app.app_context():
        base_url = 'http://localhost:8000'
        google_domain = 'clubstack1.me'
        office_domain = 'disnis.me'
        if os.environ.get('DOMAIN') == 'GOOGLE':
            domain = google_domain
        elif os.environ.get('DOMAIN') == 'OFFICE':
            domain = office_domain
        else:
            raise Exception('DOMAIN not set on environment variables')
        user = {
            'email': f"nis@{domain}",
            'domain_id': None,
            'name': "nis"
        }
        s = requests.Session()
        s.post(f'{base_url}/login', json=user)
        response = s.get(f'{base_url}/organizemeeting')
        print('Get all meeting requests - ', response.status_code, response.reason)
        if response.status_code == 200:
            meeting_requests = response.json()['data']
            for mr_idx, mr_val in enumerate(meeting_requests):
                response = s.delete(f"{base_url}/organizemeeting?id={mr_val['id']}")
                print(f'Delete meeting request [{mr_idx + 1}] - ', response.status_code, response.reason)
                if response.status_code != 200:
                    raise Exception(f'Could not delete the meeting.\n{response.text}')
            print("🧹  Meetings were deleted")
        else:
            raise Exception(f'Could not get all the meetings.\n{response.text}')
        s.get(f'{base_url}/logout')


def deletereservations():
    app = create_app()
    with app.app_context():
        base_url = 'http://localhost:8000'
        s = get_session()
        user_admin = s.query(m.User.name, m.User.email, m.User.admin).filter_by(admin=True).first()
        if not user_admin:
            raise Exception(f'There is not an admin user on DB.')
        user = {
            'email': user_admin.email,
            'domain_id': None,
            'name': user_admin.name
        }
        s = requests.Session()
        s.post(f'{base_url}/login', json=user)
        response = s.get(f'{base_url}/reservation')
        print('Get all reservations - ', response.status_code, response.reason)
        if response.status_code == 200:
            reservations = response.json()['data']
            for r_idx, r_val in enumerate(reservations):
                response = s.delete(f"{base_url}/reservation?id={r_val['id']}")
                print(f'Delete reservation [{r_idx + 1}] - ', response.status_code, response.reason)
                if response.status_code != 200:
                    raise Exception(f'Could not delete the reservation.\n{response.text}')
            print("🧹  Reservations were deleted")
        else:
            raise Exception(f'Could not get all the reservations.\n{response.text}')
        s.get(f'{base_url}/logout')


def generatemeetings():
    app = create_app()
    with app.app_context():
        base_url = 'http://localhost:8000'
        google_domain = 'clubstack1.me'
        office_domain = 'disnis.me'
        if os.environ.get('DOMAIN') == 'GOOGLE':
            domain = google_domain
        elif os.environ.get('DOMAIN') == 'OFFICE':
            domain = office_domain
        else:
            raise Exception('DOMAIN not set on environment variables')
        user = {
            'email': f"nis@{domain}",
            'domain_id': None,
            'name': "nis"
        }
        meeting_1_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-10",
            "end": "2021-12-10",
            "time_start": "09:00",
            "time_end": "11:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 55,
            "meeting_room_type": "physical",
            "building_id": 1,
            "features": {
                "ventanas": 2
            }
        }
        meeting_2_req = {
            "emails": [
                f"nis@{domain}",
                f"nahue@{domain}"
            ],
            "start": "2021-12-10",
            "end": "2021-12-10",
            "time_start": "10:00",
            "time_end": "11:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 45,
            "meeting_room_type": "physical",
            "building_id": 1,
            "features": {
                "proyector": 1
            }
        }
        meeting_3_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}"
            ],
            "start": "2021-12-13",
            "end": "2021-12-13",
            "time_start": "09:00",
            "time_end": "12:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_4_req = {
            "emails": [
                f"chris@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-13",
            "end": "2021-12-13",
            "time_start": "11:00",
            "time_end": "16:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 300,
            "meeting_room_type": "virtual"
        }
        meeting_5_req = {
            "emails": [
                f"nahue@{domain}",
                f"profesor4@{domain}"
            ],
            "start": "2021-12-13",
            "end": "2021-12-13",
            "time_start": "15:00",
            "time_end": "18:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_6_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}"
            ],
            "start": "2021-12-14",
            "end": "2021-12-14",
            "time_start": "12:00",
            "time_end": "15:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_7_req = {
            "emails": [
                f"chris@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-14",
            "end": "2021-12-14",
            "time_start": "14:00",
            "time_end": "18:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 240,
            "meeting_room_type": "virtual"
        }
        meeting_8_req = {
            "emails": [
                f"nahue@{domain}",
                f"profesor4@{domain}"
            ],
            "start": "2021-12-14",
            "end": "2021-12-14",
            "time_start": "09:00",
            "time_end": "13:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 240,
            "meeting_room_type": "virtual"
        }
        meeting_9_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}"
            ],
            "start": "2021-12-15",
            "end": "2021-12-15",
            "time_start": "11:00",
            "time_end": "15:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 240,
            "meeting_room_type": "virtual"
        }
        meeting_10_req = {
            "emails": [
                f"chris@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-15",
            "end": "2021-12-15",
            "time_start": "09:00",
            "time_end": "12:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_11_req = {
            "emails": [
                f"nahue@{domain}",
                f"profesor4@{domain}"
            ],
            "start": "2021-12-15",
            "end": "2021-12-15",
            "time_start": "16:00",
            "time_end": "18:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 120,
            "meeting_room_type": "virtual"
        }
        meeting_12_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}"
            ],
            "start": "2021-12-16",
            "end": "2021-12-16",
            "time_start": "12:00",
            "time_end": "15:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_13_req = {
            "emails": [
                f"chris@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-16",
            "end": "2021-12-16",
            "time_start": "14:00",
            "time_end": "18:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 240,
            "meeting_room_type": "virtual"
        }
        meeting_14_req = {
            "emails": [
                f"nahue@{domain}",
                f"profesor4@{domain}"
            ],
            "start": "2021-12-16",
            "end": "2021-12-16",
            "time_start": "09:00",
            "time_end": "13:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 240,
            "meeting_room_type": "virtual"
        }
        meeting_15_req = {
            "emails": [
                f"nis@{domain}",
                f"uli@{domain}"
            ],
            "start": "2021-12-17",
            "end": "2021-12-17",
            "time_start": "09:00",
            "time_end": "12:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }
        meeting_16_req = {
            "emails": [
                f"chris@{domain}",
                f"banche@{domain}"
            ],
            "start": "2021-12-17",
            "end": "2021-12-17",
            "time_start": "11:00",
            "time_end": "16:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 300,
            "meeting_room_type": "virtual"
        }
        meeting_17_req = {
            "emails": [
                f"nahue@{domain}",
                f"profesor4@{domain}"
            ],
            "start": "2021-12-17",
            "end": "2021-12-17",
            "time_start": "15:00",
            "time_end": "18:00",
            "timezone": "America/Argentina/Buenos_Aires",
            "duration": 180,
            "meeting_room_type": "virtual"
        }

        s = requests.Session()
        s.post(f'{base_url}/login', json=user)
        _meeting_http_request(s, base_url, meeting_1_req, "")
        _meeting_http_request(s, base_url, meeting_2_req, "")
        _meeting_http_request(s, base_url, meeting_3_req, 1)
        _meeting_http_request(s, base_url, meeting_4_req, 2)
        _meeting_http_request(s, base_url, meeting_5_req, 3)
        _meeting_http_request(s, base_url, meeting_6_req, 4)
        _meeting_http_request(s, base_url, meeting_7_req, 5)
        _meeting_http_request(s, base_url, meeting_8_req, 6)
        _meeting_http_request(s, base_url, meeting_9_req, 7)
        _meeting_http_request(s, base_url, meeting_10_req, 8)
        _meeting_http_request(s, base_url, meeting_11_req, 9)
        _meeting_http_request(s, base_url, meeting_12_req, 10)
        _meeting_http_request(s, base_url, meeting_13_req, 11)
        _meeting_http_request(s, base_url, meeting_14_req, 12)
        _meeting_http_request(s, base_url, meeting_15_req, 13)
        _meeting_http_request(s, base_url, meeting_16_req, 14)
        _meeting_http_request(s, base_url, meeting_17_req, 15)
        s.get(f'{base_url}/logout')
        print("✨  Meetings were made")


def makereservations():
    app = create_app()
    with app.app_context():
        base_url = 'http://localhost:8000'
        google_domain = 'clubstack1.me'
        office_domain = 'disnis.me'
        if os.environ.get('DOMAIN') == 'GOOGLE':
            domain = google_domain
        elif os.environ.get('DOMAIN') == 'OFFICE':
            domain = office_domain
        else:
            raise Exception('DOMAIN not set on environment variables')
        user_chris = {
            'email': f"chris@{domain}",
            'domain_id': None,
            'name': "chris"
        }
        user_nahue = {
            'email': f"nahue@{domain}",
            'domain_id': None,
            'name': "nahue"
        }
        s = requests.Session()
        s.post(f'{base_url}/login', json=user_chris)
        _reservation_http_request(s, base_url)
        s.get(f'{base_url}/logout')
        s.post(f'{base_url}/login', json=user_nahue)
        _reservation_http_request(s, base_url)
        s.get(f'{base_url}/logout')
        print("✨  Reservations were made")


# noinspection LongLine
@db.command()
def fillweek():
    app = create_app()
    with app.app_context():
        service_credentials = get_service_credentials_or_abort_with_http_500()
        cman = CalendarManager(config=service_credentials)
        google_domain = 'clubstack1.me'
        office_domain = 'disnis.me'
        if os.environ.get('DOMAIN') == 'GOOGLE':
            domain = google_domain
        elif os.environ.get('DOMAIN') == 'OFFICE':
            domain = office_domain
        # CHRIS EVENTS
        event = _create_event(cman, 'chris', "2021-12-13T08:00:00-03:00", "2021-12-13T14:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user chris.')
        event = _create_event(cman, 'chris', "2021-12-14T13:00:00-03:00", "2021-12-14T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user chris.')
        event = _create_event(cman, 'chris', "2021-12-15T08:00:00-03:00", "2021-12-15T15:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user chris.')
        event = _create_event(cman, 'chris', "2021-12-16T10:00:00-03:00", "2021-12-16T16:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user chris.')
        event = _create_event(cman, 'chris', "2021-12-17T08:00:00-03:00", "2021-12-17T13:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user chris.')
        # NIS EVENTS
        event = _create_event(cman, 'nis', "2021-12-13T15:00:00-03:00", "2021-12-13T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nis.')
        event = _create_event(cman, 'nis', "2021-12-14T08:00:00-03:00", "2021-12-14T13:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nis.')
        event = _create_event(cman, 'nis', "2021-12-15T16:00:00-03:00", "2021-12-15T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nis.')
        event = _create_event(cman, 'nis', "2021-12-16T08:00:00-03:00", "2021-12-16T16:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nis.')
        event = _create_event(cman, 'nis', "2021-12-17T13:00:00-03:00", "2021-12-17T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nis.')
        # ULI EVENTS
        event = _create_event(cman, 'uli', "2021-12-13T12:00:00-03:00", "2021-12-13T16:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user uli.')
        event = _create_event(cman, 'uli', "2021-12-14T13:00:00-03:00", "2021-12-14T17:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user uli.')
        event = _create_event(cman, 'uli', "2021-12-15T12:00:00-03:00", "2021-12-15T15:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user uli.')
        # event = _create_event(cman, 'uli', "2021-12-16T08:00:00-03:00", "2021-12-16T14:00:00-03:00", domain)
        # if not event:
        #     raise Exception(f'Could not create the event for user uli.')
        event = _create_event(cman, 'uli', "2021-12-17T08:00:00-03:00", "2021-12-17T14:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user uli.')
        # NAHUE EVENTS
        event = _create_event(cman, 'nahue', "2021-12-13T08:00:00-03:00", "2021-12-13T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nahue.')
        event = _create_event(cman, 'nahue', "2021-12-14T08:00:00-03:00", "2021-12-14T13:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nahue.')
        event = _create_event(cman, 'nahue', "2021-12-15T16:00:00-03:00", "2021-12-15T17:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nahue.')
        event = _create_event(cman, 'nahue', "2021-12-16T15:00:00-03:00", "2021-12-16T18:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nahue.')
        event = _create_event(cman, 'nahue', "2021-12-17T10:00:00-03:00", "2021-12-17T16:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user nahue.')
        # BANCHE EVENTS
        event = _create_event(cman, 'banche', "2021-12-13T12:00:00-03:00", "2021-12-13T13:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user banche.')
        event = _create_event(cman, 'banche', "2021-12-14T08:00:00-03:00", "2021-12-14T16:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user banche.')
        event = _create_event(cman, 'banche', "2021-12-15T13:00:00-03:00", "2021-12-15T15:00:00-03:00", domain)
        # if not event:
        #     raise Exception(f'Could not create the event for user banche.')
        # event = _create_event(cman, 'banche', "2021-12-16T08:00:00-03:00", "2021-12-16T14:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user banche.')
        event = _create_event(cman, 'banche', "2021-12-17T10:00:00-03:00", "2021-12-17T17:00:00-03:00", domain)
        if not event:
            raise Exception(f'Could not create the event for user banche.')
        print("✨  All events were created")


def _delete_meetings_and_reservations():
    print("🛠  Trying to delete the meetings")
    deletemeetings()
    print("🛠  Trying to delete the reservations")
    deletereservations()


def _meeting_http_request(session, base_url, meeting_request, summary):
    meeting = {
        "emails": None,
        "start": None,
        "end": None,
        "meeting_request_id": None,
        "summary": "Reunion hecha con script",
        "description": "Esta reunion se hizo con un script",
        "duration": None,
        "meeting_room_type": None,
        "meeting_room_id": None,
        "members_conflicts": []
    }
    response = session.post(f'{base_url}/organizemeeting', json=meeting_request)
    print('Meeting request - ', response.status_code, response.reason)
    if response.status_code == 200 and response.json()['data']:
        resp = response.json()['data'][0]
        meeting['summary'] = f"Reunion {summary}"
        if resp['meeting_room_type'] != 'virtual':
            sala = get_model_by_id(resp['meeting_room'].get('id'), m.MeetingRoom, "Meeting Room").name
            meeting['meeting_room_id'] = resp['meeting_room'].get('id')
            meeting['summary'] = f"Reunion en {sala}"
        meeting['emails'] = resp['emails']
        meeting['start'] = resp['start']
        meeting['end'] = resp['end']
        meeting['meeting_request_id'] = resp['meeting_request_id']
        meeting['duration'] = resp['duration']
        meeting['meeting_room_type'] = resp['meeting_room_type']
    else:
        raise Exception(f'Could not create the meeting.\n{response.text}')

    response = session.post(f'{base_url}/organizemeeting/confirm', json=meeting)
    print('Meeting - ', response.status_code, response.reason)
    if response.status_code != 200:
        raise Exception(f'Could not create the meeting.\n{response.text}')


def _reservation_http_request(session, base_url):
    reservation = {
        "date": "2021-12-13",
        "working_space_id": 1  # Sector IT[id]
    }
    response = session.post(f'{base_url}/reservation', json=reservation)
    print('Reservation - ', response.status_code, response.reason)
    if response.status_code != 200:
        raise Exception(f'Could not make the reservation.\n{response.text}')


def _create_event(cman, name, start, end, domain):
    return cman.create_event(
        email=f"{name}@{domain}",
        calendar_id=f"{name}@{domain}",
        event_summary="Evento generado con un script",
        event_start=start,
        event_end=end,
        event_description="Este evento se hizo con un script",
        event_attendees=[],
        meeting_room_type="placeholder",
        meeting_room_calendar_id=None
    )


if __name__ == "__main__":
    db()
