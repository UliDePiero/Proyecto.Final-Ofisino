from marshmallow import validates, ValidationError, validates_schema, Schema, fields
from marshmallow.validate import Length

from app.blueprints.building.schemas import BuildingSchema
from app.blueprints.helpers import (
    get_model_by_id,
    check_working_space_name_is_unique_for_building_id,
    custom_error_messages,
    exists_boxes_in_the_working_space,
    actual_box_capacity_working_space
)
from app.persistence.models.building_model import Building
from app.persistence.models.working_space_model import WorkingSpace
from app.persistence.session import get_session


class WorkingSpaceSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    building_id = fields.Int(required=True, error_messages=custom_error_messages)
    area = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)
    square_meters_per_box = fields.Int(required=False, error_messages=custom_error_messages)


class WorkingSpaceId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class WorkingSpaceIdResponse(Schema):
    data = fields.Nested(WorkingSpaceId)


class WorkingSpaceResponse(Schema):
    data = fields.Nested(WorkingSpaceSchema)


class WorkingSpaceListResponse(Schema):
    data = fields.List(fields.Nested(WorkingSpaceSchema))


class WorkingSpaceSchemaWithBuilding(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    building = fields.Nested(BuildingSchema, required=True, error_messages=custom_error_messages)
    area = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)
    square_meters_per_box = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)


class WorkingSpaceResponseWithBuilding(Schema):
    data = fields.Nested(WorkingSpaceSchemaWithBuilding)


class WorkingSpaceListResponseWithBuilding(Schema):
    data = fields.List(fields.Nested(WorkingSpaceSchemaWithBuilding))


class QueryInputGetWorkingSpace(Schema):
    id = fields.Int(required=False, error_messages=custom_error_messages)
    building_id = fields.Int(required=False, error_messages=custom_error_messages)

    @validates("id")
    def validate_working_space_id(self, id):
        get_model_by_id(id, WorkingSpace, "Working Space")

    @validates("building_id")
    def validate_building_id(self, building_id):
        get_model_by_id(building_id, Building, "Building")


class QueryInputPostWorkingSpace(Schema):
    building_id = fields.Int(required=True, error_messages=custom_error_messages)
    area = fields.Int(required=True, error_messages=custom_error_messages)
    square_meters_per_box = fields.Int(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)
    description = fields.String(load_default=None, required=False, error_messages=custom_error_messages)

    @validates("building_id")
    def check_building_id(self, building_id):
        get_model_by_id(building_id, Building, "Building")

    @validates("area")
    def area_cannot_be_cero(self, area):
        if area == 0:
            raise ValidationError("El area no puede ser 0")

    @validates("square_meters_per_box")
    def square_meters_per_box_cannot_be_cero(self, square_meters_per_box):
        if square_meters_per_box == 0:
            raise ValidationError("El metros cuadrados por box no puede ser 0")

    @validates_schema
    def _check_square_meters_per_box_less_than_area(self, data, **kwargs):
        if data["square_meters_per_box"] > data["area"]:
            raise ValidationError("El metro cuadrado por box no pueden ser mayor al area del "
                                  "espacio de trabajo")

    @validates_schema
    def _check_uniques_name_and_building(self,  data, **kwargs):
        if get_session().query(WorkingSpace).filter_by(
            name=data["name"],
            building_id=data["building_id"]
        ).one_or_none() is not None:
            building_name = get_model_by_id(data["building_id"], Building, "Building").name
            raise ValidationError(f"Ya existe un espacio de trabajo con el nombre: {data['name']}"
                                  f" en el edificio {building_name}.")


class QueryInputDeleteWorkingSpace(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)

    @validates("id")
    def validate_working_space_id(self, id):
        get_model_by_id(id, WorkingSpace, "Working Space")
        exists_boxes_in_the_working_space(id)


class QueryInputPutWorkingSpace(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    area = fields.Int(required=False, error_messages=custom_error_messages)
    square_meters_per_box = fields.Int(required=False, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)
    name = fields.String(required=False, validate=Length(min=1, error=custom_error_messages["length_min"]),
                         error_messages=custom_error_messages)

    @validates("id")
    def validate_working_space_id(self, id):
        get_model_by_id(id, WorkingSpace, "Working Space")

    @validates("area")
    def area_cannot_be_cero(self, area):
        if area == 0:
            raise ValidationError("El area no puede ser 0")

    @validates("square_meters_per_box")
    def square_meters_per_box_cannot_be_cero(self, square_meters_per_box):
        if square_meters_per_box == 0:
            raise ValidationError("El metro cuadrado por box no puede ser 0")

    @validates_schema
    def _check_square_meters_per_box_less_than_area(self, data, **kwargs):
        working_space = get_session().query(WorkingSpace).filter_by(id=data["id"]).one()
        my_sq_met_per_box = working_space.square_meters_per_box
        my_area = working_space.area
        if "square_meters_per_box" in data:
            my_sq_met_per_box = data["square_meters_per_box"]
        if "area" in data:
            my_area = data["area"]
        if my_sq_met_per_box > my_area:
            raise ValidationError("El metro cuadrado por box no puede ser mayor al area del "
                                  "espacio de trabajo")

    @validates_schema
    def check_working_space_capacity_matches_boxes_constraints(self, data, **kwargs):
        working_space = get_session().query(WorkingSpace).filter_by(id=data["id"]).one()

        working_space_capacity = actual_box_capacity_working_space(working_space.id)
        my_sq_met_per_box = working_space.square_meters_per_box
        my_area = working_space.area

        if "square_meters_per_box" in data:
            my_sq_met_per_box = data["square_meters_per_box"]
        if "area" in data:
            my_area = data["area"]

        new_capacity = int(my_area / my_sq_met_per_box)
        if new_capacity < working_space_capacity:
            cantidad_boxes_a_eliminar = working_space_capacity - new_capacity
            raise ValidationError(f"Se deben eliminar {cantidad_boxes_a_eliminar} de boxes "
                                  f"para poder modificar el area con {my_area} y el metro "
                                  f"por cuadrado de {my_sq_met_per_box} ")

    @validates_schema
    def check_unique_name_on_table(self,  data, **kwargs):
        if "name" in data:
            check_working_space_name_is_unique_for_building_id(data['id'], data['name'])
