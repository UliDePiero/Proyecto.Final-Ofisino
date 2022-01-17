from marshmallow import validates, Schema, fields
from marshmallow.validate import Length

from app.blueprints.helpers import get_model_by_id, custom_error_messages
from app.persistence.models import User


class UserSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    domain_id = fields.String(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    email = fields.String(required=True, error_messages=custom_error_messages)
    avatar_url = fields.String(required=True, error_messages=custom_error_messages)
    admin = fields.Boolean(required=True, error_messages=custom_error_messages)


class UserListResponse(Schema):
    data = fields.List(fields.Nested(UserSchema))


class UserResponse(Schema):
    data = fields.Nested(UserSchema)


class QueryInputGetUser(Schema):
    id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def check_user_id(self, id):
        get_model_by_id(id, User, "User")


class QueryInputPostUser(Schema):
    domain_id = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"])
                              , error_messages=custom_error_messages)
    name = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"])
                         , error_messages=custom_error_messages)
    email = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"])
                          , error_messages=custom_error_messages)
    avatar_url = fields.String(required=True, validate=Length(
        min=1, error=custom_error_messages["length_min"]
    ), error_messages=custom_error_messages)
    admin = fields.Boolean(required=False, error_messages=custom_error_messages)
