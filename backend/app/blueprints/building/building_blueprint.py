from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.building.schemas import (
    QueryInputGetBuilding,
    QueryInputPutBuilding,
    QueryInputPostBuilding,
    QueryInputDeleteBuilding,
    BuildingResponse,
    BuildingIdResponse,
    BuildingSchemaWithOrganization,
    BuildingListResponseWithOrganization,
    BuildingResponseWithOrganization
)
from app.blueprints.helpers import ok, get_model_by_id, delete_instance_by_id, validate_admin
from app.persistence.models import Organization
from app.persistence.models.building_model import Building
from app.persistence.session import get_session

bp = Blueprint('Building', __name__, description='Operations on building')


@bp.route('/building')
class BuildingAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetBuilding, location='query')
    @bp.response(200, BuildingResponse())
    def get(self, args):
        """Get building by id"""
        building_id = args.get("id")
        if building_id is None:
            logger.info("Fetching all building")
            building_from_db = get_session().query(
                Building, Organization
            ).join(
                Building, Building.organization_id == Organization.id
            ).filter(
                Building.deleted_at.is_(None)
            ).all()
            buildings_with_organization = self._get_buildings_with_organization(building_from_db)
            response_building = BuildingListResponseWithOrganization().dump(
                {"data": BuildingSchemaWithOrganization().dump(
                    buildings_with_organization, many=True
                )}
            )
            return ok(response_building)
        else:
            building_from_db = get_session().query(
                Building, Organization
            ).join(
                Building, Building.organization_id == Organization.id
            ).filter(
                Building.id == building_id
            ).one()
            building_with_organization = self._building_as_json(building_from_db)
            logger.info(f"Fetching box con id {building_id}.")
            response_building = BuildingResponseWithOrganization().dump({"data": building_with_organization})
            return ok(response_building)

    def _get_buildings_with_organization(self, buildings):
        return [self._building_as_json(building)
                for building in buildings]

    def _building_as_json(self, building):
        return {
            'id': building.Building.id,
            'location': building.Building.location,
            'description': building.Building.description,
            'name': building.Building.name,
            'organization': building.Organization.to_dict()
        }

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPostBuilding)
    @bp.response(200, BuildingResponse())
    def post(self, args):
        """Add building to organization"""
        logger.debug("Handling add building request")
        building = Building(organization_id=args['organization_id'], location=args["location"],
                            name=args["name"], description=args["description"])
        logger.info(f"Adding edificio {building}")
        get_session().add(building)
        get_session().commit()
        return ok(BuildingResponse().dump({"data": building}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputDeleteBuilding, location='query')
    @bp.response(200, BuildingIdResponse())
    def delete(self, args):
        """Delete building from organization"""
        building_id = args["id"]
        logger.info(f"Deleting edificio {building_id}")
        delete_instance_by_id(building_id, Building, "Building")
        return ok(BuildingIdResponse().dump({"data": {"id": building_id}}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPutBuilding)
    @bp.response(200, BuildingResponse())
    def put(self, args):
        """Modify building details"""
        building = get_model_by_id(args["id"], Building, "Building")
        logger.info(f"Editing edificio {building}")

        if args.get("location") is not None:
            building.location = args["location"]
        if args.get("description") is not None:
            building.description = args["description"]
        if args.get("name") is not None:
            building.name = args["name"]

        get_session().commit()
        return ok(BuildingResponse().dump({"data": building}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
