from flask_login import current_user
from marshmallow import validates, ValidationError, validates_schema, Schema, fields

from app.blueprints.box.schemas import BoxSchema
from app.blueprints.helpers import get_model_by_id, check_date, custom_error_messages, check_not_past_date
from app.blueprints.user.schemas import UserSchema
from app.persistence.models import Box, WorkingSpace
from app.persistence.models.reservation_model import Reservation
from app.persistence.session import get_session


class ReservationSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.Date(required=True, error_messages=custom_error_messages)
    box_id = fields.Int(required=True, error_messages=custom_error_messages)
    event_id = fields.String(required=True, error_messages=custom_error_messages)


class ReservationSchemaWithUserAndBox(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    user = fields.Nested(UserSchema, required=True, error_messages=custom_error_messages)
    date = fields.String(required=True, error_messages=custom_error_messages)
    box = fields.Nested(BoxSchema, required=True, error_messages=custom_error_messages)
    event_id = fields.String(required=True, error_messages=custom_error_messages)


class ReservationResponse(Schema):
    data = fields.Nested(ReservationSchema)


class ReservationListResponseWithUserAndBox(Schema):
    data = fields.List(fields.Nested(ReservationSchemaWithUserAndBox))


class ReservationId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class ReservationIdResponse(Schema):
    data = fields.Nested(ReservationId)


class QueryInputPostReservation(Schema):
    date = fields.Date(required=True, error_messages=custom_error_messages)
    box_id = fields.Int(required=False, error_messages=custom_error_messages)
    working_space_id = fields.Int(required=False, error_messages=custom_error_messages)

    @validates("box_id")
    def check_box_id(self, box_id):
        get_model_by_id(box_id, Box, "Box")

    @validates("date")
    def check_date(self, date):
        check_date(date)

    @validates("working_space_id")
    def check_working_space_id(self, working_space_id):
        get_model_by_id(working_space_id, WorkingSpace, "Working Space")

    @validates_schema
    def _check_free_date(self, data, **kwargs):
        identique_reservation = get_session(
        ).query(
            Reservation
        ).filter_by(
            user_id=current_user.id,
            date=data['date']
        ).filter(
            Reservation.deleted_at.is_(None)
        ).one_or_none()
        if identique_reservation is not None:
            raise ValidationError("Ya existe una reserva para dicho usuario ese día")

    @validates_schema
    def check_free_box(self, data, **kwargs):
        if "box" in data:
            reserved_box = get_session(
            ).query(
                Reservation
            ).filter_by(
                box_id=data['box_id']
            ).filter(
                Reservation.date == data['date'],
                Reservation.deleted_at.is_(None),
                Box.deleted_at.is_(None)
            ).one_or_none()
            if reserved_box is not None:
                raise ValidationError(f"El box {data['box_id']}"
                                      f"se encuentra ocupado el dia {data['date']}")

    @validates_schema
    def check_working_space_id_and_box_id(self, data, **kwargs):
        if "box_id" not in data and "working_space_id" not in data:
            raise ValidationError("Se debe informar un box o en caso "
                                  "de ser automático, el espacio de trabajo.")
        if "box_id" in data and "working_space_id" in data:
            raise ValidationError("Debe elegir o un box o un espacio de trabajo.")


class QueryInputDeleteReservation(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_reservation(self, id):
        reservation = get_model_by_id(id, Reservation, "Reservation")
        check_not_past_date(reservation.date)


class QueryInputPutReservation(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.Date(required=False, error_messages=custom_error_messages)
    box_id = fields.Int(required=False, error_messages=custom_error_messages)

    @validates("id")
    def validate_reservation(self, id):
        reservation = get_model_by_id(id, Reservation, "Reservation")
        check_not_past_date(reservation.date)

    @validates("date")
    def check_date(self, date):
        check_date(date)

    @validates_schema
    def check_free_date(self, data, **kwargs):
        same_reservation = get_session(
        ).query(
            Reservation
        ).filter_by(
            user_id=current_user.id,
            date=data['date']
        ).filter(
            Reservation.id != data['id'],
            Reservation.deleted_at.is_(None)
        ).one_or_none()
        if same_reservation is not None:
            raise ValidationError("Ya existe una reserva para dicho usuario ese día")

    @validates_schema
    def check_free_box(self, data, **kwargs):
        if 'box_id' not in data:
            return

        if 'date' in data:
            reservation_date = data['date']
        else:
            reservation = get_session().query(Reservation).filter_by(id=data['id']).one()
            reservation_date = reservation.date

        reserved_box = get_session().\
            query(Reservation).\
            filter_by(box_id=data['box_id']).\
            filter(Reservation.date == reservation_date,
                   Reservation.id != data['id'],
                   Reservation.deleted_at.is_(None)
                   ).\
            one_or_none()
        if reserved_box is not None:
            raise ValidationError(f"El box {data['box_id']} "
                                  f"se encuentra ocupado el dia {reservation_date}")
