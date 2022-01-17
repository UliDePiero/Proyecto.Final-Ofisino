from marshmallow import validates, Schema, fields, ValidationError

from app.blueprints.helpers import get_model_by_id, custom_error_messages
from app.blueprints.meeting_room.schemas import MeetingRoomSchemaWithBuilding
from app.blueprints.user.schemas import UserSchema
from app.persistence.models import User, MeetingRoom, MeetingRequest, Meeting
from app.persistence.session import get_session


class MeetingSchemaWithMeetingRoomAndUser(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    requester_user = fields.Nested(UserSchema, required=True, error_messages=custom_error_messages)
    attendees = fields.List(fields.Nested(UserSchema), required=True, error_messages=custom_error_messages)
    meeting_room = fields.Nested(
        MeetingRoomSchemaWithBuilding,
        required=True, error_messages=custom_error_messages
    )
    date_start = fields.String(required=True, error_messages=custom_error_messages)
    date_end = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)
    event = fields.String(required=True, error_messages=custom_error_messages)


class MeetingSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_room_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.String(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)


class MeetingResponseWithMeetingRoomAndUser(Schema):
    data = fields.Nested(MeetingSchemaWithMeetingRoomAndUser)


class MeetingResponse(Schema):
    data = fields.Nested(MeetingSchema)


class MeetingListResponse(Schema):
    data = fields.List(fields.Nested(MeetingSchema), error_messages=custom_error_messages)


class MeetingId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingIdResponse(Schema):
    data = fields.Nested(MeetingId)


class QueryInputGetMeeting(Schema):
    id = fields.Int(error_messages=custom_error_messages)
    meeting_request_id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_id(self, id):
        get_model_by_id(id, Meeting, "Meeting")

    @validates("meeting_request_id")
    def validate_meeting_meeting_request_id(self, meeting_request_id):
        get_model_by_id(meeting_request_id, MeetingRequest, "Meeting Request")
        instance = get_session().query(Meeting).filter_by(meeting_request_id=meeting_request_id).\
            filter(Meeting.deleted_at.is_(None)).one_or_none()
        if instance is None:
            raise ValidationError(f"No hay una reunion asociada a esta solicitud.")


class QueryInputPostMeeting(Schema):
    user_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_room_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.DateTime(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    summary = fields.String(required=False, error_messages=custom_error_messages)

    @validates("user_id")
    def check_user_id(self, user_id):
        get_model_by_id(user_id, User, "User")

    @validates("meeting_room_id")
    def check_meeting_room_id(self, meeting_room_id):
        get_model_by_id(meeting_room_id, MeetingRoom, "Meeting room")

    @validates("meeting_request_id")
    def check_meeting_request_id(self, meeting_request_id):
        get_model_by_id(meeting_request_id, MeetingRequest, "Meeting request")
