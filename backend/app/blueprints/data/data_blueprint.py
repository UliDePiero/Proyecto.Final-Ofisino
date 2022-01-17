import logging
import os
from pathlib import Path

import pandas as pd
from flask import send_file, after_this_request
from flask_login import login_required
from flask_smorest import Blueprint

from app.blueprints.helpers import get_model_by_id, status_meeting_request, validate_admin
from app.blueprints.meeting_request.schemas import MeetingRequestResponse
from app.blueprints.reservation.reservation_blueprint import get_reservations_with_user_and_box
from app.blueprints.reservation.schemas import ReservationListResponseWithUserAndBox
from app.persistence.models import Reservation, User, Box, WorkingSpace, MeetingRequest
from app.persistence.session import get_session

PARENT = Path(__file__).absolute().parent
FILE_DATA = PARENT / 'file_data.xlsx'

bp = Blueprint('Data', __name__, description='Get data')


@bp.route("/data/reservation")
@login_required
@validate_admin
@bp.response(200, ReservationListResponseWithUserAndBox())
def data_reservations():
    """Get reservations data """
    base_reservations_query = get_session().query(
        Reservation, User, Box
    ).join(
        User, User.id == Reservation.user_id
    ).join(
        Box, Box.id == Reservation.box_id
    ).filter(
        Reservation.deleted_at.is_(None)
    )
    reservations_from_db = base_reservations_query.all()
    reservations_with_user_and_box = get_reservations_with_user_and_box(reservations_from_db)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(FILE_DATA)
        except Exception as error:
            logging.error("Error al borrar o cerrar el archivo")
        return response

    return save_reservations_data_to_file(reservations_with_user_and_box)


def save_reservations_data_to_file(reservations_list):
    for reservation in reservations_list:
        reservation["Nro. de box"] = reservation["box"]["id"]
        reservation["Nombre de box"] = reservation["box"]["name"]
        reservation["Nombre de espacio de trabajo"] = get_model_by_id(reservation["box"]["working_space_id"],
                                                                      WorkingSpace,
                                                                      "Working Space").name

        reservation["Tipo de usuario"] = "ADMIN" if reservation["user"]["admin"] else "USER"
        reservation["Email de usuario"] = reservation["user"]["email"]
        reservation["Nombre de usuario"] = reservation["user"]["name"]

        reservation.pop("box")
        reservation.pop("user")
    df = pd.DataFrame(reservations_list)
    df.to_excel(FILE_DATA)
    return send_file(FILE_DATA)


@bp.route("/data/meetingrequest")
@login_required
@validate_admin
@bp.response(200, MeetingRequestResponse())
def data_meetings_request():
    meetings_request = get_session().\
        query(MeetingRequest).\
        filter(MeetingRequest.status != status_meeting_request["in_process"]).\
        all()

    @after_this_request
    def remove_file(response):
        try:
            os.remove(FILE_DATA)
        except Exception as error:
            logging.error("Error al borrar o cerrar el archivo")
        return response

    return save_meeting_request_file(get_meetings_request(meetings_request))


def save_meeting_request_file(meetings_request):
    df = pd.DataFrame(meetings_request)
    df.to_excel(FILE_DATA)
    return send_file(FILE_DATA)


def get_meetings_request(meetings_request):
    return [
        {
            'Usuario solicitante': get_model_by_id(meeting_request.user_id, User, "User").name,
            'Estado': meeting_request.status,
            'Titulo de la reunion': meeting_request.summary,
            'Fecha de inicio de rango': meeting_request.conditions.get('start'),
            'Fecha de fin de rango': meeting_request.conditions.get('end'),
            'Hora de inicio de rango': meeting_request.conditions.get('time_start'),
            'Hora de fin de rango': meeting_request.conditions.get('time_end'),
            'Zona horaria': meeting_request.conditions.get('timezone'),
            'Duracion (en mins)': meeting_request.conditions.get('duration'),
            'Tipo de reunion': meeting_request.conditions.get('meeting_room_type'),
            'Invitados': meeting_request.conditions.get('emails')
        }
        for meeting_request in meetings_request
    ]
