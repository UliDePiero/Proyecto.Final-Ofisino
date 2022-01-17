from marshmallow import validates, ValidationError, validates_schema, Schema, fields
from marshmallow.validate import Length

from app.blueprints.helpers import (
    get_model_by_id,
    check_building_name_is_unique_for_organization_id,
    custom_error_messages,
    exists_working_spaces_in_the_building,
    exists_meeting_rooms_in_the_building
)
from app.blueprints.organization.schemas import OrganizationSchema
from app.persistence.models.building_model import Building
from app.persistence.models.organization_model import Organization
from app.persistence.session import get_session


class BuildingSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    organization_id = fields.String(required=True, error_messages=custom_error_messages)
    location = fields.String(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)


class BuildingResponse(Schema):
    data = fields.Nested(BuildingSchema)


class BuildingId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class BuildingIdResponse(Schema):
    data = fields.Nested(BuildingId)


class BuildingSchemaWithOrganization(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    organization = fields.Nested(OrganizationSchema, required=True, error_messages=custom_error_messages)
    location = fields.String(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)


class BuildingListResponseWithOrganization(Schema):
    data = fields.List(fields.Nested(BuildingSchemaWithOrganization))


class BuildingResponseWithOrganization(Schema):
    data = fields.Nested(BuildingSchemaWithOrganization)


class QueryInputGetBuilding(Schema):
    id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def validate_building_id(self, id):
        get_model_by_id(id, Building, "Building")


class QueryInputPostBuilding(Schema):
    organization_id = fields.Int(required=True, error_messages=custom_error_messages)
    location = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"]),
                             error_messages=custom_error_messages)
    name = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)

    @validates("organization_id")
    def check_organization_id(self, organization_id):
        get_model_by_id(organization_id, Organization, "Organization")

    @validates_schema
    def check_unique_name_and_organization(self,  data, **kwargs):
        if get_session().query(Building).filter_by(
            name=data["name"],
            organization_id=data["organization_id"]
        ).one_or_none() is not None:
            organization_name = get_model_by_id(data["organization_id"], Organization, "Organization").name
            raise ValidationError(f"Ya existe un edificio con el nombre: {data['name']}"
                                  f" en la organización {organization_name}.")


class QueryInputDeleteBuilding(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_building_id(self, id):
        get_model_by_id(id, Building, "Building")
        exists_working_spaces_in_the_building(id)
        exists_meeting_rooms_in_the_building(id)


class QueryInputPutBuilding(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    location = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"])
                             , error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    name = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)

    @validates("id")
    def validate_building_id(self, id):
        get_model_by_id(id, Building, "Building")

    @validates_schema
    def check_unique_name_on_table(self,  data, **kwargs):
        if "name" in data:
            check_building_name_is_unique_for_organization_id(data['id'], data['name'])
