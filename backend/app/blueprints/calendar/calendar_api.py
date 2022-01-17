import dataclasses
import os
import random
from datetime import datetime
from pathlib import Path
from string import Template
from typing import Optional

from flask import jsonify, redirect
from flask_login import current_user, login_required
from flask_smorest import Blueprint

from app.api_credentials import get_service_credentials_or_abort_with_http_500
from app.blueprints.email_sender import send_email
from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    get_model_by_email,
    get_models_by_email_list,
    status_meeting_request,
    delete_instance_by_id,
    delete_instances_by_id_list
)
from app.blueprints.meeting.meeting_blueprint import MeetingAPI
from app.blueprints.meeting_request.meeting_request_blueprint import MeetingRequestAPI
from app.blueprints.meeting_request_user.meeting_request_user_blueprint import MeetingRequestUserAPI
from app.blueprints.meeting_user.meeting_user_blueprint import MeetingUserAPI
from app.calendar_class import CalendarManager, DOMAIN_ADMIN_ACC
from app.persistence.models.meeting_model import Meeting
from app.persistence.models.meeting_request_model import MeetingRequest
from app.persistence.models.meeting_request_user_model import MeetingRequestUser
from app.persistence.models.meeting_room_model import MeetingRoom
from app.persistence.models.meeting_user_model import MeetingUser
from app.persistence.models.user_model import User
from app.persistence.session import get_session
from .schemas import (
    QueryInputGetSlots,
    QueryInputPostOrganizeMeeting,
    QueryInputPostOrganizeMeetingConfirm,
    QueryInputPostOrganizeMeetingCancel,
    QueryInputEmailAccept,
    QueryInputEmailDecline,
    OrganizeMeetingIdResponse,
    OrganizeMeetingConfirmResponse,
    OrganizeMeetingListResponse,
    OrganizeMeetingSchema,
    SlotsResponse,
    ParticipantsListResponse,
    ParticipantsSchema,
    CalendarResponse,
    AllCalendarsResponse,
    CalendarsResponse,
    SlotsSchema,
    AllCalendarsSchema,
    CalendarsSchema,
)

bp = Blueprint('Calendar', __name__, description='Interact with Calendar api')


@dataclasses.dataclass
class MeetingOption:
    emails: list[str]
    meeting_request_id: int
    meeting_room_type: str
    meeting_room: Optional[dict]
    start: str
    end: str
    duration: int
    kind: str
    missing_features: dict
    members_conflicts: list[dict]

    def to_dict(self):
        option = {
            "emails": self.emails,
            "meeting_request_id": self.meeting_request_id,
            "meeting_room_type": self.meeting_room_type,
            "meeting_room": self.meeting_room,
            "start": self.start,
            "end": self.end,
            "duration": self.duration,
            "kind": self.kind,
            "missing_features": self.missing_features,
            "members_conflicts": self.members_conflicts
        }
        return option


@bp.route('/orgmembers')
@bp.response(200, ParticipantsListResponse())
def get_participants():
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    users = cman.get_users()
    data = [
        {
            'name': user['name']['fullName'],
            'email': user['primaryEmail']
        }
        for user in users
        if user['primaryEmail'] != DOMAIN_ADMIN_ACC
    ]
    return ok(ParticipantsListResponse().dump(
        {"data": ParticipantsSchema().dump(data, many=True)})
    )


@bp.route('/busy-slots')
@bp.arguments(QueryInputGetSlots, location='query')
@bp.response(200, SlotsResponse())
def get_busy_slots(get_args):
    """Get busy slots of a calendar
    ---
    Las fechas deben tener el formato 2021-07-11T03:00:00-03:00
    """
    args = _parse_calendar_args(get_args)
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    slots_response = cman.get_busy_slots_for_calendar(
        args['email'],
        args['cal_id'],
        args['start'],
        args['end'],
        tz=cman.BS_AS_TIMEZONE
    )
    busy_slots = [slot.to_dict() for slot in slots_response]
    return ok(SlotsResponse().dump(
        {"data": SlotsSchema().dump(busy_slots, many=True)})
    )


@bp.route('/free-slots')
@bp.arguments(QueryInputGetSlots, location='query')
@bp.response(200, SlotsResponse())
def get_free_slots(get_args):
    """Get free slots of a calendar

    ---
    Las fechas deben tener el formato 2021-07-11T03:00:00-03:00"""
    args = _parse_calendar_args(get_args)
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    free_slots_response = cman.get_free_slots_for_calendar(
        args['email'],
        args['cal_id'],
        args['start'],
        args['end']
    )
    free_slots = [slot.to_dict() for slot in free_slots_response]
    return ok(SlotsResponse().dump(
        {"data": SlotsSchema().dump(free_slots, many=True)})
    )


@bp.route('/calendars')
@bp.response(200, AllCalendarsResponse())
def get_calendars_json():
    """Get all the users calendars"""
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    resp = cman.get_all_users_calendars()
    return ok(AllCalendarsResponse().dump(
        {"data": AllCalendarsSchema().dump(resp, many=True)})
    )


@bp.route('/calendars/email/<string:email>')
@bp.response(200, CalendarsResponse())
def get_calendars_for_user_json(email):
    """Get all the calendars for a user"""
    get_model_by_email(email)
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    resp = cman.get_calendars(email)
    return ok(CalendarsResponse().dump(
        {"data": CalendarsSchema().dump(resp, many=True)})
    )


@bp.route('/calendars/email/<string:email>/<string:cal_id>')
@bp.response(200, CalendarResponse())
def get_calendar_for_user_json(email, cal_id):
    """Get calendar info for a user"""
    get_model_by_email(email)
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    resp = cman.get_calendar_by_id(email, cal_id)
    return ok(CalendarResponse().dump({"data": resp}))


@bp.route('/organizemeeting', methods=['POST'])
@login_required
@bp.arguments(QueryInputPostOrganizeMeeting)
@bp.response(200, OrganizeMeetingListResponse())
def generate_meeting_multiple_calendars(args):
    """Coordinate meeting between multiple calendars
    ---
    Devuelve una reunion creada y agrega el evento al calendario de los usuarios
    La duracion de la reunion tiene que ser multiplo de 5"""
    me: User = current_user
    data = []
    attendees = args['emails'].copy()
    attendees_without_org = args['emails'].copy()
    if me.email in attendees:
        organizer = me.email
    else:
        organizer = attendees[0]
    attendees_without_org.remove(organizer)
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    users = cman.get_users()
    users_by_email = {
        user['primaryEmail']: user['name']['fullName']
        for user in users
    }
    s = get_session()
    users_from_db = s.query(User.email).filter(User.deleted_at.is_(None)).all()
    users_to_db = []
    emails_from_db = [u.email for u in users_from_db]
    for email in args['emails']:
        if email not in emails_from_db and email in users_by_email.keys():
            user_from_db = User(email=email, name=users_by_email[email])
            users_to_db.append(user_from_db)
        elif email not in users_by_email.keys():
            return jsonify({"errors": f"El email: {email} no pertenece al dominio de la organizacion."}), 400
    s.add_all(users_to_db)
    s.commit()

    kind = "ok"
    missing_features = {}
    slot_list = []
    slot_list_conf = []
    meeting_room_id = None
    meeting_room_id_conf = None
    meeting_room = None
    conflicting_member = {}
    if args['meeting_room_type'] != 'virtual':
        meeting_rooms = _filter_meeting_rooms(args['features'], args['emails'], args['building_id'])
        slot_list, meeting_room_id = _found_available_room(
            cman=cman,
            meeting_rooms=meeting_rooms.copy(),
            emails=args['emails'],
            start=args['start'],
            end=args['end'],
            time_start=args['time_start'],
            time_end=args['time_end'],
            duration=args['duration'],
            timezone=args['timezone']
        )
        if not meeting_room_id:
            for a in attendees_without_org:
                attendees.remove(a)
                slot_list_conf, meeting_room_id_conf = _found_available_room(
                    cman=cman,
                    meeting_rooms=meeting_rooms.copy(),
                    emails=attendees,
                    start=args['start'],
                    end=args['end'],
                    time_start=args['time_start'],
                    time_end=args['time_end'],
                    duration=args['duration'],
                    timezone=args['timezone']
                )
                if meeting_room_id_conf:
                    conflicting_member = {
                        'name': get_model_by_email(a).name,
                        'email': a
                    }
                    break
                else:
                    attendees.append(a)

            kind = "missing_features"
            meeting_rooms = get_session().query(MeetingRoom).filter(
                MeetingRoom.capacity >= len(args['emails']),
                MeetingRoom.deleted_at.is_(None),
                MeetingRoom.building_id == args['building_id']
            ).all()
            slot_list, meeting_room_id = _found_available_room(
                cman=cman,
                meeting_rooms=meeting_rooms.copy(),
                emails=args['emails'],
                start=args['start'],
                end=args['end'],
                time_start=args['time_start'],
                time_end=args['time_end'],
                duration=args['duration'],
                timezone=args['timezone']
            )
            if meeting_room_id:
                missing_features = _get_missing_features(meeting_room_id, args['features'])
    elif args['meeting_room_type'] == 'virtual':
        slot_list = cman.organize_meeting(
            cals=args['emails'],
            start=args['start'],
            end=args['end'],
            time_start=args['time_start'],
            time_end=args['time_end'],
            duration=args['duration'],
            meeting_room=args['meeting_room_type'],
            tz=args['timezone']
        )
        if not slot_list:
            for a in attendees_without_org:
                attendees.remove(a)
                slot_list_conf = cman.organize_meeting(
                    cals=attendees,
                    start=args['start'],
                    end=args['end'],
                    time_start=args['time_start'],
                    time_end=args['time_end'],
                    duration=args['duration'],
                    meeting_room=args['meeting_room_type'],
                    tz=args['timezone']
                )
                if slot_list_conf:
                    conflicting_member = {
                        'name': get_model_by_email(a).name,
                        'email': a
                    }
                    break
                else:
                    attendees.append(a)

    slots_found = [slot.to_dict() for slot in slot_list]
    slots_found_conf = [slot.to_dict() for slot in slot_list_conf]

    if slots_found or slots_found_conf:
        status = status_meeting_request['in_process']
    else:
        status = status_meeting_request['no_results']
    cond_dict = {
        "start": args['start'].isoformat(),
        "end": args['end'].isoformat(),
        "time_start": args['time_start'].isoformat(timespec='minutes'),
        "time_end": args['time_end'].isoformat(timespec='minutes'),
        "timezone": args['timezone'],
        "duration": args['duration'],
        "emails": args['emails'],
        "meeting_room_type": args['meeting_room_type']
    }
    meeting_request_to_db = {
        "user_id": me.id,
        "conditions": cond_dict,
        "status": status,
    }
    resp_meeting_request_dict = _add_request_to_db(class_=MeetingRequestAPI, args=meeting_request_to_db)
    users = get_models_by_email_list(args['emails'], User, "User")
    meeting_request_users_to_db = [
        {
            "meeting_request_id": resp_meeting_request_dict['id'],
            "user_id": user.id
        }
        for user in users
    ]
    _add_request_to_db(class_=MeetingRequestUserAPI, args=meeting_request_users_to_db)
    if slots_found:
        if meeting_room_id:
            meeting_room = get_model_by_id(meeting_room_id, MeetingRoom, "Meeting Room").to_dict()
        option_ok_or_missing_features = MeetingOption(
            kind=kind,
            emails=args['emails'],
            meeting_request_id=resp_meeting_request_dict['id'],
            meeting_room_type=args['meeting_room_type'],
            meeting_room=meeting_room,
            start=slots_found[0]['start'],
            end=slots_found[0]['end'],
            duration=args['duration'],
            missing_features=missing_features,
            members_conflicts=[]
        )
        data.append(option_ok_or_missing_features.to_dict())
    if slots_found_conf:
        if meeting_room_id_conf:
            meeting_room = get_model_by_id(meeting_room_id_conf, MeetingRoom, "Meeting Room").to_dict()
        option_conflicts = MeetingOption(
            kind="conflicts",
            emails=args['emails'],
            meeting_request_id=resp_meeting_request_dict['id'],
            meeting_room_type=args['meeting_room_type'],
            meeting_room=meeting_room,
            start=slots_found_conf[0]['start'],
            end=slots_found_conf[0]['end'],
            duration=args['duration'],
            missing_features={},
            members_conflicts=[conflicting_member]
        )
        data.append(option_conflicts.to_dict())

    return ok(OrganizeMeetingListResponse().dump(
        {"data": OrganizeMeetingSchema().dump(data, many=True)})
    )


@bp.route('/organizemeeting/confirm', methods=['POST'])
@login_required
@bp.arguments(QueryInputPostOrganizeMeetingConfirm)
@bp.response(200, OrganizeMeetingConfirmResponse())
def confirm_meeting_request(args):
    """Confirm the meeting request between multiple calendars
        ---
        Devuelve una reunion creada y agrega el evento al calendario de los usuarios"""
    me: User = current_user
    attendees = args['emails']
    if me.email in attendees:
        organizer = me.email
    else:
        organizer = attendees[0]
    if args['summary'] is None or args['summary'] == "":
        args['summary'] = 'Reunion Ofisino'
    mr = get_model_by_id(args['meeting_request_id'], MeetingRequest, "meeting_request")
    mr.summary = args['summary']
    get_session().commit()
    if args.get('members_conflicts'):
        _build_email_for_member(args, me.name, me.email, organizer)
        return jsonify({"data": "Email enviado al miembro que tiene el conflicto."})

    data = _create_meeting(
        attendees=attendees,
        organizer=organizer,
        requester_id=me.id,
        summary=args['summary'],
        meeting_room_type=args['meeting_room_type'],
        meeting_room_id=args['meeting_room_id'],
        start=args['start'].isoformat(),
        end=args['end'].isoformat(),
        description=args['description'],
        meeting_request_id=args['meeting_request_id'],
        duration=args['duration']
    )
    return ok(OrganizeMeetingConfirmResponse().dump({"data": data}))


@bp.route('/organizemeeting/cancel', methods=['POST'])
@bp.arguments(QueryInputPostOrganizeMeetingCancel)
@bp.response(200, OrganizeMeetingIdResponse())
def cancel_meeting_request(args):
    mr = get_model_by_id(args['meeting_request_id'], MeetingRequest, "meeting_request")
    mr.status = status_meeting_request["cancelled"]

    delete_instance_by_id(mr.id, MeetingRequest, "Meeting Request")
    users = get_session().query(MeetingRequestUser.id).filter_by(meeting_request_id=mr.id).all()
    id_list = [user.id for user in users]
    delete_instances_by_id_list(id_list, MeetingRequestUser)
    return ok(OrganizeMeetingIdResponse().dump({"data": {"id": mr.id}}))


@bp.route('/email/accept', methods=['GET'])
@bp.arguments(QueryInputEmailAccept, location='query')
def email_accept(args):
    mr = get_model_by_id(args.get('meeting_request_id'), MeetingRequest, "Meeting request")
    if mr.status == status_meeting_request["pending"]:
        config = get_service_credentials_or_abort_with_http_500()
        cman = CalendarManager(config=config)
        cman.delete_event(DOMAIN_ADMIN_ACC, args.get('event_blocker_id'), send_updates=False)
        events = args['events_org'].split("-") + args['events_mem'].split("-")
        events = list(filter(None, events))
        user = get_model_by_email(args.get('member_email'))
        for e in events:
            meeting_model = get_session().query(Meeting.id).filter_by(event=e).one_or_none()
            if meeting_model and user:
                meeting_user_model = get_session().query(MeetingUser).filter_by(
                    meeting_id=meeting_model.id
                ).filter(MeetingUser.user_id == user.id).one_or_none()
                if meeting_user_model:
                    delete_instance_by_id(meeting_user_model.id, MeetingUser, "Meeting User")
            cman.delete_event(args.get('member_email'), e)
        requester_id = get_model_by_email(args.get('requester')).id
        if args['summary'] == "None" or args['summary'] == "":
            args['summary'] = 'Reunion Ofisino'
        if args['meeting_room_id'] == "None":
            args['meeting_room_id'] = None
        _create_meeting(
            attendees=mr.conditions['emails'],
            organizer=args.get('organizer'),
            requester_id=requester_id,
            summary=args['summary'],
            meeting_room_type=mr.conditions['meeting_room_type'],
            meeting_room_id=args['meeting_room_id'],
            start=args['start'],
            end=args['end'],
            description=args['description'],
            meeting_request_id=args['meeting_request_id'],
            duration=mr.conditions['duration']
        )
    return redirect(os.environ.get('EP_MEETING'), code=302)


@bp.route('/email/decline', methods=['GET'])
@bp.arguments(QueryInputEmailDecline, location='query')
def email_decline(args):
    mr = get_model_by_id(args.get('meeting_request_id'), MeetingRequest, "Meeting request")
    if mr.status == status_meeting_request["pending"]:
        config = get_service_credentials_or_abort_with_http_500()
        cman = CalendarManager(config=config)
        cman.delete_event(DOMAIN_ADMIN_ACC, args.get('event_blocker_id'))
        if args.get('summary') == "None" or args.get('summary') == "":
            args['summary'] = 'Reunion Ofisino'
        meeting_data = (f"La reunión: {args['summary']} la habías planificado para la fecha: "
                        f"{datetime.fromisoformat(args['start']).strftime('%H:%M, %B %d, %Y')}")
        path = Path(__file__).resolve().parent.parent
        email_html = path / 'email_organizemeeting_decline.html'
        with email_html.open('r') as f:
            email_dec_body = Template(f.read()).safe_substitute(
                member_name=args.get('member'),
                meeting_data=meeting_data,
                EP_ORGANIZEMEETING=os.environ.get('EP_ORGANIZEMEETING')
            )
        send_email(
            email=args.get('requester'),
            name=args.get('requester'),
            subject="OFISINO - Respuesta a tu solicitud de reunion",
            body=email_dec_body
        )
        mr = get_model_by_id(args['meeting_request_id'], MeetingRequest, "meeting_request")
        mr.status = status_meeting_request["declined"]
        get_session().commit()
    return redirect(os.environ.get('EP_MEETING'), code=302)


def _filter_meeting_rooms(features, emails, building_id):
    meeting_rooms = get_session().query(
        MeetingRoom
    ).filter(
        MeetingRoom.capacity >= len(emails),
        MeetingRoom.deleted_at.is_(None),
        MeetingRoom.building_id == building_id
    ).all()
    valid_meeting_rooms = []
    for meeting_room in meeting_rooms:
        valid = True
        for key in features:
            if meeting_room.features[key] < features[key]:
                valid = False
                break
        if valid:
            valid_meeting_rooms.append(meeting_room)

    return valid_meeting_rooms


def _found_available_room(cman, meeting_rooms, emails, start, end, time_start, time_end, duration, timezone):
    max_loop = len(meeting_rooms)
    for i in range(max_loop):
        meeting_room = random.choice(meeting_rooms)
        meeting_rooms.remove(meeting_room)
        slot_list = cman.organize_meeting(
            cals=emails,
            start=start,
            end=end,
            time_start=time_start,
            time_end=time_end,
            duration=duration,
            meeting_room=meeting_room.calendar,
            tz=timezone
        )
        if slot_list:
            return slot_list, meeting_room.id
    return [], None


def _get_missing_features(meeting_room_id, requested_features):
    meeting_room = get_model_by_id(meeting_room_id, MeetingRoom, "Meeting Room")
    missing_features = {
        key: requested_features[key] - meeting_room.features[key]
        for key in requested_features
        if meeting_room.features[key] < requested_features[key]
    }
    return missing_features


def _create_meeting(
        attendees: list,
        organizer: str,
        requester_id: int,
        summary: str,
        meeting_room_type: str,
        meeting_room_id: Optional[int],
        start: str,
        end: str,
        description: str,
        meeting_request_id: int,
        duration: int
):
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    users = get_models_by_email_list(attendees, User, "User")
    if meeting_room_type != 'virtual':
        meeting_room_calendar_id = get_model_by_id(meeting_room_id, MeetingRoom, "meeting_room").calendar
    else:
        meeting_room_calendar_id = None
    event_id = cman.create_event(
        email=organizer,
        calendar_id=organizer,
        event_summary=summary,
        event_start=start,
        event_end=end,
        event_description=description,
        event_attendees=attendees,
        meeting_room_type=meeting_room_type,
        meeting_room_calendar_id=meeting_room_calendar_id
    )
    meeting_to_db = {
        "user_id": requester_id,
        "meeting_room_id": meeting_room_id,
        "meeting_request_id": meeting_request_id,
        "date": start,
        "duration": duration,
        "description": description,
        "summary": summary,
        "event": event_id
    }
    resp_meeting_dict = _add_request_to_db(class_=MeetingAPI, args=meeting_to_db)
    meeting_users_to_db = [
        {
            "meeting_id": resp_meeting_dict['id'],
            "user_id": user.id
        }
        for user in users
    ]
    _add_request_to_db(class_=MeetingUserAPI, args=meeting_users_to_db)
    mr = get_model_by_id(meeting_request_id, MeetingRequest, "meeting_request")
    mr.status = status_meeting_request["accepted"]
    get_session().commit()
    return resp_meeting_dict


def _build_email_for_member(args, requester_name, requester_email, organizer):
    email_to = args.get('members_conflicts')[0]
    member = get_model_by_email(email_to)
    member_name = member.name
    member_email = member.email
    config = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=config)
    events = cman.get_events_between_time(
        email=email_to,
        start=args.get('start').isoformat(),
        end=args.get('end').isoformat()
    )
    events_ids_org = ""
    events_ids_mem = ""
    events_summ_org = ""
    events_summ_mem = ""
    for e in events:
        if e.get('organizer')['email'] == email_to:
            if events_ids_org != "":
                events_ids_org = f"{events_ids_org}-{e.get('id')}"
                events_summ_org = (f"{events_summ_org}<br>{e.get('summary')}"
                                   f"<a href={e.get('htmlLink')}> Ver evento </a>")
            else:
                events_ids_org = e.get('id')
                events_summ_org = (f"Los eventos que están a tu cargo y cancelarías son los siguientes:<br>"
                                   f"{e.get('summary')}<a href={e.get('htmlLink')}> Ver evento </a>")
        else:
            if events_ids_mem != "":
                events_ids_mem = f"{events_ids_mem}-{e.get('id')}"
                events_summ_mem = (f"{events_summ_mem}<br>{e.get('summary')}"
                                   f"<a href={e.get('htmlLink')}> Ver evento </a>")
            else:
                events_ids_mem = e.get('id')
                events_summ_mem = (f"Los eventos a los que faltarías son los siguientes:<br>"
                                   f"{e.get('summary')}<a href={e.get('htmlLink')}> Ver evento </a>")

    if args['meeting_room_type'] != 'virtual':
        meeting_room_calendar_id = (get_model_by_id(args['meeting_room_id'], MeetingRoom, "meeting_room")
                                    .calendar)
    else:
        meeting_room_calendar_id = None
    event_blocker_id = cman.create_event(
        email=DOMAIN_ADMIN_ACC,
        calendar_id=DOMAIN_ADMIN_ACC,
        event_summary="Posible futura reunión Ofisino",
        event_description="Espacio reservado para una posible reunión a concretarse",
        event_start=args.get('start').isoformat(),
        event_end=args.get('end').isoformat(),
        event_attendees=args['emails'],
        meeting_room_type="placeholder",
        meeting_room_calendar_id=meeting_room_calendar_id
    )
    path = Path(__file__).resolve().parent.parent
    if os.environ.get('DOMAIN').casefold() == "GOOGLE".casefold():
        email_html = path / 'email_organizemeeting_conflicts.html'
    else:
        email_html = path / 'email_organizemeeting_conflicts_outlook.html'
    with email_html.open('r') as f:
        email_conf_body = Template(f.read()).safe_substitute(
            requester_name=requester_name.title(),
            member_name=member_name.title(),
            member_email=member_email,
            requester_email=requester_email,
            organizer=organizer,
            summary=args.get('summary'),
            description=args.get('description'),
            meeting_request_id=args.get('meeting_request_id'),
            meeting_room_id=args.get('meeting_room_id'),
            start=args.get('start').isoformat(),
            end=args.get('end').isoformat(),
            events_org=events_ids_org,
            events_org_summ=events_summ_org,
            events_mem=events_ids_mem,
            events_mem_summ=events_summ_mem,
            event_blocker_id=event_blocker_id,
            EP_EMAIL_ACCEPT=os.environ.get('EP_EMAIL_ACCEPT'),
            EP_EMAIL_DECLINE=os.environ.get('EP_EMAIL_DECLINE')
        )
    send_email(email_to, email_to, "OFISINO - Un usuario requiere tu respuesta", email_conf_body)
    mr = get_model_by_id(args.get('meeting_request_id'), MeetingRequest, "Meeting request")
    mr.status = status_meeting_request["pending"]
    get_session().commit()


def _add_request_to_db(class_, args):
    resp = class_.insert_to_db(self=class_, args=args)
    return resp['data']


def _parse_calendar_args(args):
    """email, calId, start, end"""
    email = args.get("email")
    cal_id = args.get("calId")
    start = args.get("start")
    end = args.get("end")

    args_dic = {
        'email': email,
        'cal_id': cal_id,
        'start': start,
        'end': end
    }
    return args_dic


@bp.errorhandler(500)
@bp.errorhandler(422)
@bp.errorhandler(404)
@bp.errorhandler(400)
def handle_error(err):
    if err.code == 500:
        return jsonify({"errors": err.description}), err.code
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
