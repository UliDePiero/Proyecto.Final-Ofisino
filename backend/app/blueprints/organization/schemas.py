from marshmallow import validates, ValidationError, Schema, fields, validates_schema
from marshmallow.validate import Length

from app.blueprints.helpers import get_model_by_id, check_organization_name_is_unique, custom_error_messages
from app.persistence.models.organization_model import Organization
from app.persistence.session import get_session


class OrganizationSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)


class OrganizationId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class OrganizationListResponse(Schema):
    data = fields.List(fields.Nested(OrganizationSchema))


class OrganizationIdResponse(Schema):
    data = fields.Nested(OrganizationId)


class OrganizationResponse(Schema):
    data = fields.Nested(OrganizationSchema)


class QueryInputGetOrganization(Schema):
    id = fields.Int(error_messages=custom_error_messages)

    @validates("id")
    def check_organization_id(self, id):
        get_model_by_id(id, Organization, "Organization")


class QueryInputPostOrganization(Schema):
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)

    @validates("name")
    def _check_unique_name(self, name):
        if get_session().query(Organization).filter_by(name=name).one_or_none() is not None:
            raise ValidationError(f"Ya existe una organización con el nombre: {name}.")


class QueryInputDeleteOrganization(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_organization_id(self, id):
        get_model_by_id(id, Organization, "Organization")


class QueryInputPutOrganization(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    name = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"]))

    @validates("id")
    def validate_organization_id(self, id):
        get_model_by_id(id, Organization, "Organization")

    @validates_schema
    def check_unique_name_on_table(self,  data, **kwargs):
        if "name" in data:
            check_organization_name_is_unique(data['id'], data['name'])
