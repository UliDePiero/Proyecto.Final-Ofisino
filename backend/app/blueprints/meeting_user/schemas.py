from marshmallow import validates, Schema, fields

from app.blueprints.helpers import get_model_by_id, custom_error_messages
from app.persistence.models import User, Meeting, MeetingUser


class MeetingUserSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingUserResponse(Schema):
    data = fields.Nested(MeetingUserSchema)


class MeetingUserListResponse(Schema):
    data = fields.List(fields.Nested(MeetingUserSchema), error_messages=custom_error_messages)


class MeetingUserId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class MeetingUserIdResponse(Schema):
    data = fields.Nested(MeetingUserId)


class QueryInputGetMeetingUser(Schema):
    id = fields.Int(error_messages=custom_error_messages)
    user_id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_user_id(self, id):
        get_model_by_id(id, MeetingUser, "Meeting user")

    @validates("user_id")
    def validate_meeting_request_user_user_id(self, user_id):
        get_model_by_id(user_id, User, "User")


class QueryInputPostMeetingUser(Schema):
    meeting_id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("meeting_id")
    def check_meeting_id(self, meeting_id):
        get_model_by_id(meeting_id, Meeting, "Meeting")

    @validates("user_id")
    def check_user_id(self, user_id):
        get_model_by_id(user_id, User, "User")


class QueryInputDeleteMeetingUser(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_meeting_user_id(self, id):
        get_model_by_id(id, MeetingUser, "Meeting user")
