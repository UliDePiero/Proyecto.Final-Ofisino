from marshmallow import validates, ValidationError, validates_schema, Schema, fields
from marshmallow.validate import Length

from app.blueprints.building.schemas import BuildingSchema
from app.blueprints.helpers import get_model_by_id, check_meeting_room_name_is_unique_for_building_id, \
    custom_error_messages, exists_meetings_for_this_meeting_room
from app.persistence.models.building_model import Building
from app.persistence.models.meeting_room_model import MeetingRoom
from app.persistence.session import get_session


class FeaturesSchema(Schema):
    aire_acondicionado = fields.Int(load_default=0, error_messages=custom_error_messages)
    computadoras = fields.Int(load_default=0, error_messages=custom_error_messages)
    proyector = fields.Int(load_default=0, error_messages=custom_error_messages)
    ventanas = fields.Int(load_default=0, error_messages=custom_error_messages)
    sillas = fields.Int(load_default=0, error_messages=custom_error_messages)
    mesas = fields.Int(load_default=0, error_messages=custom_error_messages)


class MeetingRoomSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    building_id = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    capacity = fields.Int(required=True, error_messages=custom_error_messages)
    features = fields.Nested(FeaturesSchema, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)
    calendar = fields.String(required=True, error_messages=custom_error_messages)


class MeetingRoomResponse(Schema):
    data = fields.Nested(MeetingRoomSchema)


class MeetingRoomSchemaWithBuilding(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    building = fields.Nested(BuildingSchema, required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    capacity = fields.Int(required=True, error_messages=custom_error_messages)
    features = fields.Nested(FeaturesSchema, required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)
    calendar = fields.String(required=True, error_messages=custom_error_messages)


class MeetingRoomListResponseWithBuilding(Schema):
    data = fields.List(fields.Nested(MeetingRoomSchemaWithBuilding))


class MeetingRoomId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingRoomIdResponse(Schema):
    data = fields.Nested(MeetingRoomId)


class MeetingRoomResponseWithBuilding(Schema):
    data = fields.Nested(MeetingRoomSchemaWithBuilding)


class QueryInputGetMeetingRoom(Schema):
    id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_room_id(self, id):
        get_model_by_id(id, MeetingRoom, "Meeting Room")


class QueryInputPostMeetingRoom(Schema):
    building_id = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)
    capacity = fields.Int(required=True, error_messages=custom_error_messages)
    features = fields.Nested(FeaturesSchema, required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)

    @validates("building_id")
    def check_building_id(self, building_id):
        get_model_by_id(building_id, Building, "Building")

    @validates_schema
    def _check_name_and_building(self,  data, **kwargs):
        if get_session().query(MeetingRoom).filter_by(
            name=data["name"],
            building_id=data["building_id"]
        ).one_or_none() is not None:
            building_name = get_model_by_id(data["building_id"], Building, "Building").name
            raise ValidationError(f"Ya existe una sala con el nombre: {data['name']}"
                                  f" en el edificio {building_name}.")


class QueryInputDeleteMeetingRoom(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_room_id(self, id):
        get_model_by_id(id, MeetingRoom, "Meeting Room")
        exists_meetings_for_this_meeting_room(id)


class QueryInputPutMeetingRoom(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    capacity = fields.Int(required=False, error_messages=custom_error_messages)
    features = fields.Nested(FeaturesSchema, required=False, error_messages=custom_error_messages)
    name = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_room_id(self, id):
        get_model_by_id(id, MeetingRoom, "Meeting Room")

    @validates_schema
    def check_unique_name_on_table(self,  data, **kwargs):
        if "name" in data:
            check_meeting_room_name_is_unique_for_building_id(data['id'], data['name'])
