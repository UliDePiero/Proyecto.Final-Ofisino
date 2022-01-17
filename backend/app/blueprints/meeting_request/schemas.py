from marshmallow import validates, Schema, fields

from app.blueprints.helpers import get_model_by_id, custom_error_messages, admin_or_author_required
from app.persistence.models import User, MeetingRequest


class ConditionsSchema(Schema):
    """meeting_room_type must be 'virtual' or another string representing a physical room"""
    start = fields.String(error_messages=custom_error_messages)
    end = fields.String(error_messages=custom_error_messages)
    time_start = fields.String(error_messages=custom_error_messages)
    time_end = fields.String(error_messages=custom_error_messages)
    timezone = fields.String(error_messages=custom_error_messages)
    duration = fields.Int(error_messages=custom_error_messages)
    meeting_room_type = fields.String(error_messages=custom_error_messages)
    emails = fields.List(
        fields.String(error_messages=custom_error_messages),
        error_messages=custom_error_messages
    )


class MeetingRequestSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)
    conditions = fields.Nested(ConditionsSchema)
    status = fields.String(required=True, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)


class MeetingRequestResponse(Schema):
    data = fields.Nested(MeetingRequestSchema)


class MeetingRequestListResponse(Schema):
    data = fields.List(fields.Nested(MeetingRequestSchema))


class MeetingRequestId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingRequestIdResponse(Schema):
    data = fields.Nested(MeetingRequestId)


class QueryInputGetMeetingRequest(Schema):
    id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_request_id(self, id):
        get_model_by_id(id, MeetingRequest, "Meeting request")


class QueryInputDeleteMeetingRequest(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_request_id(self, id):
        get_model_by_id(id, MeetingRequest, "Meeting request")
        admin_or_author_required(id, MeetingRequest, "meeting_request")
