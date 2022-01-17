from flask import jsonify, make_response
from flask.views import MethodView
from flask_login import login_required, current_user
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.api_extra_functions import create_all_date_event, delete_event
from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    delete_instance_by_id,
    search_empty_boxes,
    user_create_reservation_or_user_is_admin
)
from app.blueprints.reservation.schemas import (
    QueryInputPutReservation,
    QueryInputPostReservation,
    QueryInputDeleteReservation,
    ReservationResponse,
    ReservationIdResponse,
    ReservationListResponseWithUserAndBox,
    ReservationSchemaWithUserAndBox,
)
from app.persistence.models import User, Box
from app.persistence.models.reservation_model import Reservation
from app.persistence.session import get_session

bp = Blueprint('Reservation', __name__, description='Operations on reservation')


def get_reservations_with_user_and_box(reservations):
    return [
        {
            'id': reservation.Reservation.id,
            'date': reservation.Reservation.date,
            'user': reservation.User.to_dict(),
            'box': reservation.Box.to_dict(),
            'event_id': reservation.Reservation.event_id
        }
        for reservation in reservations
    ]


@bp.route('/reservation')
class ReservationAPI(MethodView):

    @login_required
    @bp.response(200, ReservationListResponseWithUserAndBox())
    def get(self):
        """Get reservas
        Return reservations corresponding to the logged user.
        If user is admin, return all the reservations
        """
        me: User = current_user

        base_reservations_query = get_session().query(
            Reservation, User, Box
        ).join(
            User, User.id == Reservation.user_id
        ).join(
            Box, Box.id == Reservation.box_id
        ).filter(
            Reservation.deleted_at.is_(None)
        )
        if not me.admin:
            base_reservations_query = base_reservations_query.filter(
                Reservation.user_id == me.id
            )
        reservations_from_db = base_reservations_query.all()
        reservations_with_user_and_box = get_reservations_with_user_and_box(reservations_from_db)
        response_reservation = ReservationListResponseWithUserAndBox().dump(
            {"data": ReservationSchemaWithUserAndBox().dump(
                reservations_with_user_and_box, many=True
            )}
        )
        return ok(response_reservation)

    @login_required
    @bp.arguments(QueryInputPostReservation)
    @bp.response(200, ReservationResponse())
    def post(self, args):
        """Add a reservation"""
        logger.debug("Handling add reservation request")
        if args.get("box_id") is not None:
            the_box_id = args.get("box_id")
        else:
            empty_boxes = search_empty_boxes(args['working_space_id'], args["date"])
            if not empty_boxes:
                return jsonify({"errors": {"json": {"_schema": ["No existen boxes vacios "
                                                                "en el espacio de trabajo para la fecha "
                                                                "solicitada."]}}}), 405
            the_box_id = empty_boxes.pop(0)["id"]

        reservation = Reservation(user_id=current_user.id, date=args["date"], box_id=the_box_id)
        logger.info(f"Adding reservation {reservation}")

        user = get_model_by_id(current_user.id, User, "User")
        event_id = create_all_date_event(user.email,
                                         reservation.box_id,
                                         args['date'],
                                         args['date'])
        reservation.event_id = event_id
        get_session().add(reservation)
        get_session().commit()
        return ok(ReservationResponse().dump({"data": reservation}))

    @login_required
    @bp.arguments(QueryInputDeleteReservation, location='query')
    @bp.response(200, ReservationIdResponse())
    def delete(self, args):
        """Delete a reservation by id"""
        reservation_id = args["id"]
        reservation = get_model_by_id(reservation_id, Reservation, "Reservation")
        if not user_create_reservation_or_user_is_admin(current_user, reservation.user_id):
            return make_response(jsonify({"error": "No puede eliminar la reserva "
                                                   "ya que no es administrador ni creador de la reserva"})
                                 , 405)

        logger.info(f"Deleting reservation {reservation_id}")
        reservation = get_model_by_id(reservation_id, Reservation, "Reservation")
        delete_instance_by_id(reservation_id, Reservation, "Reservation")
        user = get_model_by_id(reservation.user_id, User, "User")
        delete_event(user.email, reservation.event_id)
        return ok(ReservationIdResponse().dump({"data": {"id": reservation_id}}))

    @login_required
    @bp.arguments(QueryInputPutReservation)
    @bp.response(200, ReservationResponse())
    def put(self, args):
        """Modify reservation details"""
        reservation = get_model_by_id(args["id"], Reservation, "Reservation")
        if not user_create_reservation_or_user_is_admin(current_user, reservation.user_id):
            return make_response(jsonify({"error": "No puede eliminar la reserva "
                                                   "ya que no es administrador ni creador de la reserva"}),
                                 405)
        logger.info(f"Editing reservation {reservation}")
        check_modify = False
        if args.get("date"):
            reservation.date = args.get("date")
            check_modify = True
        if args.get("box_id"):
            reservation.box_id = args.get("box_id")
            check_modify = True
        if check_modify:
            user = get_model_by_id(reservation.user_id, User, "User")
            delete_event(user.email, reservation.event_id)
            event_id = create_all_date_event(user.email,
                                             reservation.box_id,
                                             reservation.date,
                                             reservation.date)
            reservation.event_id = event_id
        get_session().commit()
        return ok(ReservationResponse().dump({"data": reservation}))


@bp.route('/reservation/own')
@login_required
@bp.response(200, ReservationListResponseWithUserAndBox())
def get_own_reservations():
    """Get reservas
    Return reservations corresponding to the logged user
    """
    reservations_from_db = get_session().query(
        Reservation, User, Box
    ).join(
        User, User.id == Reservation.user_id
    ).join(
        Box, Box.id == Reservation.box_id
    ).filter(
        Reservation.deleted_at.is_(None),
        Reservation.user_id == current_user.id
    ).all()
    reservations_with_user_and_box = get_reservations_with_user_and_box(reservations_from_db)
    response_reservation = ReservationListResponseWithUserAndBox().dump(
        {"data": ReservationSchemaWithUserAndBox().dump(
            reservations_with_user_and_box, many=True
        )}
    )
    return ok(response_reservation)


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
