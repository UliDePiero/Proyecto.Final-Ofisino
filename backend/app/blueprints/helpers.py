import datetime
import os
from datetime import timezone

import pytz
from flask import jsonify
from flask_login import current_user
from marshmallow import ValidationError

from app.blueprints.email_sender import send_email, create_box_email_format, create_meeting_room_email_format
from app.persistence.models import (
    Building,
    WorkingSpace,
    MeetingRoom,
    User,
    Box,
    Organization, Reservation, Meeting
)
from app.persistence.session import get_session

"""Tested with Int, String, Datetime, List, Length, Nested"""
custom_error_messages = {
    "required": "Faltan datos para el campo obligatorio.",
    "null": "El campo no puede ser nulo.",
    "validator_failed": "Valor no valido.",
    "invalid": "No es un tipo de dato valido.",
    "invalid_utf8": "No es un tipo utf-8 valido.",
    "type": "Tipo invalido.",
    "format": "El valor ingresado no tiene el formato correcto.",
    "length_min": "El campo rellenado es mas corto que el minimo requerido: {min}.",
    "length_max": "El campo rellenado es mas largo que el maximo requerido: {max}.",
    "length_all": "El campo debe tener una longitud entre {min} y {max}.",
    "length_equal": "El campo debe tener una longitud igual a {equal}.",
}

"""Possible statuses of a meeting request"""
status_meeting_request = {
    "pending": "Pendiente",
    "in_process": "En proceso",
    "no_results": "Sin resultados",
    "declined": "Rechazada",
    "accepted": "Aceptada",
    "cancelled": "Cancelada"
}

TZ = os.environ.get('SERVER_TIMEZONE') or "America/Argentina/Buenos_Aires"


def ok(response_dict: dict, status=200):
    return jsonify(response_dict), status, {'ContentType': 'application/json'}


def get_model_by_id(instance_id, table, table_name):
    instance = get_session().query(table).filter_by(id=instance_id).one_or_none()
    if instance is None or instance.deleted_at is not None:
        raise ValidationError(f"El id {instance_id} de la tabla {table_name} no existe.")
    return instance


def get_models_by_id_list(instance_id_list, table):
    return get_session().query(table).filter(table.id.in_(instance_id_list), table.deleted_at.is_(None)).all()


def delete_instance_by_id(instance_id, table, table_name):
    instance = get_model_by_id(instance_id, table, table_name)
    instance.deleted_at = pytz.timezone(TZ).fromutc(datetime.datetime.utcnow())
    get_session().commit()


def delete_instances_by_id_list(instance_id_list, table):
    instances = get_models_by_id_list(instance_id_list, table)
    tz = pytz.timezone(TZ).fromutc(datetime.datetime.utcnow())
    for i in instances:
        i.deleted_at = tz
    get_session().commit()


def exists_future_reservations_for_the_box(box_id):
    box = get_session().query(
        Reservation
    ).filter_by(
        box_id=box_id
    ).filter(
        Reservation.date >= datetime.date.today(),
        Box.deleted_at.is_(None),
        Reservation.deleted_at.is_(None)
    ).all()
    if len(box) != 0:
        raise ValidationError(f"El box posee reservas futuras, debe eliminarlas antes de eliminar el box.")


def exists_boxes_in_the_working_space(working_space_id):
    box = get_session().query(
        Box
    ).filter_by(
        working_space_id=working_space_id
    ).filter(
        Box.deleted_at.is_(None)
    ).all()
    if len(box) != 0:
        raise ValidationError(f"El espacio de trabajo posee boxes asociados,"
                              f"debe eliminarlos antes de eliminar el espacio de trabajo.")


def exists_working_spaces_in_the_building(building_id):
    working_space = get_session().query(
        WorkingSpace
    ).filter_by(
        building_id=building_id
    ).filter(
        WorkingSpace.deleted_at.is_(None)
    ).all()
    if len(working_space) != 0:
        raise ValidationError(f"El edificio posee espacios de trabajo asociados, "
                              f"debe eliminarlos antes de eliminar el edificio.")


def exists_meeting_rooms_in_the_building(building_id):
    meeting_room = get_session().query(
        MeetingRoom
    ).filter_by(
        building_id=building_id
    ).filter(
        MeetingRoom.deleted_at.is_(None)
    ).all()

    if len(meeting_room) != 0:
        raise ValidationError("El edificio posee salas de reunion asociadas, "
                              "debe eliminarlas antes de eliminar el edificio.")


def exists_meetings_for_this_meeting_room(meeting_room_id):
    meetings = get_session().query(
        Meeting
    ).filter_by(
        meeting_room_id=meeting_room_id
    ).filter(
        Meeting.deleted_at.is_(None)
    ).all()

    for meeting in meetings:
        if datetime.datetime.fromisoformat(meeting.date) >= datetime.datetime.now(timezone.utc).astimezone():
            raise ValidationError("La sala de reunion posee reuniones asociadas futuras,"
                                  " debe eliminarlas antes de eliminar la sala de reunion.")


def get_models_by_email_list(email_list, table, table_name):
    instances = get_session().query(table).filter(
        table.email.in_(email_list),
        table.deleted_at.is_(None)
    ).all()
    if not instances:
        raise ValidationError(f"Ninguno de los emails: {email_list}, existe en la tabla {table_name}.")
    if len(instances) != len(email_list):
        raise ValidationError(f"Alguno de los emails: {email_list}, no existe en la tabla {table_name}.")
    return instances


def get_model_by_email(email):
    instance = get_session().query(User).filter_by(email=email).\
        filter(User.deleted_at.is_(None)).one_or_none()
    if instance is None:
        raise ValidationError(f"El email {email} de la tabla User no existe.")

    return instance


def get_models_by_user_id(user_id, table, table_name):
    instances = get_session().query(table).filter_by(user_id=user_id).filter(table.deleted_at.is_(None)).all()

    return instances


def ckeck_name_and_building_unique(instance_id, table, name, table_name):
    instance = get_session().query(table).filter_by(name=name).filter(table.id != instance_id).one_or_none()
    if instance is not None:
        raise ValidationError(f"El nombre {name} en la tabla {table_name} ya existe.")


def check_meeting_room_name_is_unique_for_building_id(instance_id, name):
    meeting_room = get_session().query(MeetingRoom).filter_by(id=instance_id).one()
    meeting_room_same_name = get_session().query(
        MeetingRoom
    ).filter_by(
        name=name
    ).filter(
        MeetingRoom.id != instance_id,
        MeetingRoom.building_id == meeting_room.building_id,
        MeetingRoom.deleted_at.is_(None)
    ).one_or_none()
    if meeting_room_same_name is not None:
        raise ValidationError(f"Ya existe una sala de reunion en ese edificio con el nombre {name}.")


def check_working_space_name_is_unique_for_building_id(instance_id, name):
    working_space = get_session().query(WorkingSpace).filter_by(id=instance_id).one()
    working_space_same_name = get_session().query(
        WorkingSpace
    ).filter_by(
        name=name
    ).filter(
        WorkingSpace.id != instance_id,
        WorkingSpace.building_id == working_space.building_id,
        WorkingSpace.deleted_at.is_(None)
    ).one_or_none()
    if working_space_same_name is not None:
        raise ValidationError(f"Ya existe un espacio de trabajo en ese edificio con el nombre {name}.")


def check_building_name_is_unique_for_organization_id(instance_id, name):
    building = get_session().query(Building).filter_by(id=instance_id).one()
    building_same_name = get_session().query(
        Building
    ).filter_by(
        name=name
    ).filter(
        Building.id != instance_id,
        Building.organization_id == building.organization_id,
        Building.deleted_at.is_(None)
    ).one_or_none()
    if building_same_name is not None:
        raise ValidationError(f"Ya existe un edificio en esa organización con el nombre {name}.")


def check_box_name_is_unique_for_working_space_id(instance_id, name):
    box = get_session().query(Box).filter_by(id=instance_id).one()
    box_same_name = get_session().query(
        Box
    ).filter_by(
        name=name
    ).filter(
        Box.id != instance_id,
        Box.working_space_id == box.working_space_id,
        Box.deleted_at.is_(None)
    ).one_or_none()
    if box_same_name is not None:
        raise ValidationError(f"Ya existe un box en ese edificio con el nombre {name}.")


def check_organization_name_is_unique(instance_id, name):
    organization_same_name = get_session(). \
        query(Organization). \
        filter_by(name=name). \
        filter(Organization.id != instance_id, Organization.deleted_at.is_(None)). \
        one_or_none()
    if organization_same_name is not None:
        raise ValidationError(f"Ya existe una organización con el nombre {name}.")


def check_start_end(start, end, time_start, time_end):
    if start > end:
        raise ValidationError("La fecha de inicio debe ser anterior a la de fin.")
    if time_start > time_end:
        raise ValidationError("La hora de inicio debe ser anterior a la de fin.")
    elif start < datetime.date.today() or end < datetime.date.today():
        raise ValidationError("La fecha de inicio y de final debe ser mayor o igual a hoy.")


def check_dates_range_less_than_2_weeks(start, end):
    if abs(end - start).days > 14:
        raise ValidationError("El rango de fechas debe ser menor a 2 semanas.")


def check_date(date):
    my_timezone = pytz.timezone(TZ)
    my_date = my_timezone.fromutc(datetime.datetime.utcnow())
    if date < my_date.date():
        raise ValidationError("La fecha debe ser mayor o igual a hoy.")


def check_not_past_date(the_date):
    my_timezone = pytz.timezone(TZ)
    my_date = my_timezone.fromutc(datetime.datetime.utcnow())
    if the_date < my_date.date():
        raise ValidationError("No se puede borrar o modificar una reserva que ya sucedio.")


def check_box_quantity_does_not_exceed_working_space_capacity(working_space_id):
    working_space = get_session().query(WorkingSpace). \
        filter_by(id=working_space_id). \
        one()
    max_boxes = int(working_space.area / working_space.square_meters_per_box)
    if actual_box_capacity_working_space(working_space_id) == max_boxes:
        raise ValidationError("No se puede agregar un nuevo box "
                              "ya que excede a la cantidad por metro cuadrado.")


def actual_box_capacity_working_space(working_space_id):
    return len(get_session().query(Box).filter_by(working_space_id=working_space_id)
               .filter(Box.deleted_at.is_(None)).all())


def _get_boxes_with_working_space(boxes):
    return [_box_as_json_with_working_space(box)
            for box in boxes]


def _get_boxes(boxes):
    return [_box_as_json(box)
            for box in boxes]


def _box_as_json(box):
    return {
        'id': box.id,
        'name': box.name,
        'description': box.description,
        'working_space': box.working_space_id
    }


def _box_as_json_with_working_space(box):
    return {
        'id': box.Box.id,
        'name': box.Box.name,
        'description': box.Box.description,
        'working_space': box.WorkingSpace.to_dict()
    }


def search_empty_boxes(working_space_id, the_date):
    not_empty_boxes = get_session().query(
        Reservation.box_id
    ).filter(
        Box.working_space_id == working_space_id
    ).distinct(
        Reservation.box_id
    ).filter(
        Reservation.date == the_date,
        Reservation.deleted_at.is_(None)
    ).all()

    reserved_boxes_ids = [box for box, in not_empty_boxes]

    empty_boxes = get_session().query(
        Box
    ).filter(
        Box.id.not_in(reserved_boxes_ids), Box.working_space_id == working_space_id, Box.deleted_at.is_(None)
    ).all()

    return _get_boxes(empty_boxes)


def admin_or_author_required(instance_id, table, table_name):
    me: User = current_user
    instance = get_model_by_id(instance_id, table, table_name)
    if not (me.admin or instance.user_id == me.id):
        raise ValidationError("No tienes permisos para realizar esta accion.")


def send_email_to_users_with_box_reservation(box, name_before, description_before):
    if description_before == box.description and name_before == box.name:
        return
    reservations = get_session().query(
        Reservation
    ).filter_by(
        box_id=box.id
    ).filter(
        Reservation.date >= datetime.date.today(),
        Reservation.deleted_at.is_(None)
    ).all()
    emails = []
    for reservation in reservations:
        user = get_model_by_id(reservation.user_id, User, "User")
        if user.email not in emails:
            email_subject = f'Cambios en la reserva del dia {reservation.date}'
            send_email(user.email, user.name, email_subject, create_box_email_format(
                box, name_before, description_before
            ))
            emails.append(user.email)


def send_email_to_users_with_meeting_room_meetings(meeting_room, older_meeting_room):
    """formato 2021-10-21T17:25:00-03:00 """
    meetings = get_session().query(
        Meeting
    ).filter_by(
        meeting_room_id=meeting_room.id
    ).filter(
        Meeting.deleted_at.is_(None)
    ).all()

    emails = []
    for meeting in meetings:
        if datetime.datetime.fromisoformat(meeting.date) >= datetime.datetime.now(timezone.utc).astimezone():
            user = get_model_by_id(meeting.user_id, User, "User")
            if user.email not in emails:
                email_subject = f'Cambios en la sala de reunion del dia {meeting.date}'
                send_email(user.email, user.name, email_subject,
                           create_meeting_room_email_format(meeting_room, older_meeting_room))
                emails.append(user.email)


def user_create_reservation_or_user_is_admin(user, user_id_reservation):
    return user.id is user_id_reservation or user.admin


# Decorators
def validate_admin(func):
    def validate(*args, **kwargs):
        me: User = current_user
        if not me.admin:
            return jsonify({"errors": {"json": {"admin": ["No sos el administrador."]}}}), 405
        return func(*args, **kwargs)

    return validate
