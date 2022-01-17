from marshmallow import validates, Schema, fields

from app.blueprints.helpers import get_model_by_id, custom_error_messages
from app.persistence.models import User, MeetingRequest, MeetingRequestUser


class MeetingRequestUserSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingRequestUserResponse(Schema):
    data = fields.Nested(MeetingRequestUserSchema)


class MeetingRequestUserListResponse(Schema):
    data = fields.List(fields.Nested(MeetingRequestUserSchema), error_messages=custom_error_messages)


class MeetingRequestUserId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingRequestUserIdResponse(Schema):
    data = fields.Nested(MeetingRequestUserId)


class QueryInputGetMeetingRequestUser(Schema):
    id = fields.Int(error_messages=custom_error_messages)
    user_id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_request_user_id(self, id):
        get_model_by_id(id, MeetingRequestUser, "Meeting request user")

    @validates("user_id")
    def validate_meeting_request_user_user_id(self, user_id):
        get_model_by_id(user_id, User, "User")


class QueryInputPostMeetingRequestUser(Schema):
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("meeting_request_id")
    def check_meeting_request_id(self, meeting_request_id):
        get_model_by_id(meeting_request_id, MeetingRequest, "Meeting request")

    @validates("user_id")
    def check_user_id(self, user_id):
        get_model_by_id(user_id, User, "User")


class QueryInputDeleteMeetingRequestUser(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_request_user_id(self, id):
        get_model_by_id(id, MeetingRequestUser, "Meeting request user")
