from marshmallow import validates, ValidationError, validates_schema, Schema, fields
from marshmallow.validate import Length

from app.blueprints.helpers import (
    get_model_by_id,
    check_box_name_is_unique_for_working_space_id,
    check_box_quantity_does_not_exceed_working_space_capacity, custom_error_messages,
    exists_future_reservations_for_the_box
)
from app.blueprints.working_space.schemas import WorkingSpaceSchema
from app.persistence.models import Box
from app.persistence.models.working_space_model import WorkingSpace
from app.persistence.session import get_session


class BoxSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    working_space_id = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)


class BoxId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class BoxIdResponse(Schema):
    data = fields.Nested(BoxId)


class BoxResponse(Schema):
    data = fields.Nested(BoxSchema)


class BoxListResponse(Schema):
    data = fields.List(fields.Nested(BoxSchema))


class BoxSchemaWithWorkingSpace(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    working_space = fields.Nested(WorkingSpaceSchema, required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)


class BoxListResponseWithWorkingSpace(Schema):
    data = fields.List(fields.Nested(BoxSchemaWithWorkingSpace))


class BoxResponseWithWorkingSpace(Schema):
    data = fields.Nested(BoxSchemaWithWorkingSpace)


class QueryInputGetBox(Schema):
    id = fields.Int(required=False, error_messages=custom_error_messages)

    @validates("id")
    def validate_box_id(self, id):
        get_model_by_id(id, Box, "Box")


class QueryInputGetAvailableBoxes(Schema):
    working_space_id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.Date(required=True, error_messages=custom_error_messages)

    @validates("working_space_id")
    def validate_working_space_id(self, working_space_id):
        get_model_by_id(working_space_id, WorkingSpace, "WorkingSpace")


class QueryInputPostBox(Schema):
    working_space_id = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)

    @validates("working_space_id")
    def check_working_space_id(self, working_space_id):
        get_model_by_id(working_space_id, WorkingSpace, "Working Space")
        check_box_quantity_does_not_exceed_working_space_capacity(working_space_id)

    @validates_schema
    def _check_uniques_name_and_working_space(self,  data, **kwargs):
        if get_session().query(Box).filter_by(
            name=data["name"],
            working_space_id=data["working_space_id"]
        ).one_or_none() is not None:
            working_space_name = get_model_by_id(data["working_space_id"], WorkingSpace, "Working Space").name
            raise ValidationError(f"Ya existe un box con el nombre: {data['name']}"
                                  f" en el espacio de trabajo {working_space_name}.")


class QueryInputDeleteBox(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_box_id(self, id):
        get_model_by_id(id, Box, "Box")
        exists_future_reservations_for_the_box(id)


class QueryInputPutBox(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    name = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)

    @validates("id")
    def validate_box_id(self, id):
        get_model_by_id(id, Box, "Box")

    @validates_schema
    def check_unique_name_on_table(self,  data, **kwargs):
        if "name" in data:
            check_box_name_is_unique_for_working_space_id(data['id'], data['name'])
