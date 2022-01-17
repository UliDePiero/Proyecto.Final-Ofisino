from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import ok, get_model_by_id, delete_instance_by_id, validate_admin
from app.blueprints.working_space.schemas import (
    QueryInputGetWorkingSpace,
    QueryInputPutWorkingSpace,
    QueryInputPostWorkingSpace,
    QueryInputDeleteWorkingSpace,
    WorkingSpaceResponse,
    WorkingSpaceIdResponse,
    WorkingSpaceListResponseWithBuilding,
    WorkingSpaceSchemaWithBuilding,
    WorkingSpaceResponseWithBuilding,

)
from app.persistence.models import Building
from app.persistence.models.working_space_model import WorkingSpace
from app.persistence.session import get_session

bp = Blueprint('WorkingSpace', __name__, description='Operations on espacio de trabajo')


@bp.route('/workingspace')
class WorkingSpaceAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetWorkingSpace, location='query')
    @bp.response(200, WorkingSpaceResponse())
    def get(self, args):

        working_space_id = args.get("id")
        building_id = args.get("building_id")
        if working_space_id is not None:
            """Get working space by id"""
            working_space_from_db = get_session().query(
                WorkingSpace, Building
            ).join(
                WorkingSpace, WorkingSpace.building_id == Building.id
            ).filter(
                WorkingSpace.id == working_space_id,
            ).one()
            working_space_with_building = self._working_space_as_json(working_space_from_db)
            logger.info(f"Fetching working space con id {working_space_id}.")
            response_working_space = WorkingSpaceResponseWithBuilding().\
                dump({"data": working_space_with_building})
            return ok(response_working_space)

        elif building_id is not None:
            """Get working space by building id"""
            working_space_from_db = get_session().query(
                WorkingSpace, Building
            ).join(
                WorkingSpace, WorkingSpace.building_id == Building.id
            ).filter(
                Building.id == building_id,
                WorkingSpace.deleted_at.is_(None)
            ).all()

            working_space_with_building = self._get_working_spaces_with_building(working_space_from_db)
            response_working_space = WorkingSpaceListResponseWithBuilding().dump(
                {"data": WorkingSpaceSchemaWithBuilding().dump(
                    working_space_with_building, many=True
                )}
            )
            return ok(response_working_space)

        else:
            logger.info("Fetching all espacios de trabajo")
            working_space_from_db = get_session().query(
                WorkingSpace, Building
            ).join(
                WorkingSpace, WorkingSpace.building_id == Building.id
            ).filter(
                WorkingSpace.deleted_at.is_(None)
            ).all()
            working_space_with_building = self._get_working_spaces_with_building(working_space_from_db)
            response_working_space = WorkingSpaceListResponseWithBuilding().dump(
                {"data": WorkingSpaceSchemaWithBuilding().dump(
                    working_space_with_building, many=True
                )}
            )
            return ok(response_working_space)

    def _get_working_spaces_with_building(self, working_spaces):
        return [self._working_space_as_json(working_space)
                for working_space in working_spaces]

    def _working_space_as_json(self, working_space):
        return {
            'id': working_space.WorkingSpace.id,
            'area': working_space.WorkingSpace.area,
            'square_meters_per_box': working_space.WorkingSpace.square_meters_per_box,
            'name': working_space.WorkingSpace.name,
            'description': working_space.WorkingSpace.description,
            'building': working_space.Building.to_dict()
        }

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPostWorkingSpace)
    @bp.response(200, WorkingSpaceResponse())
    def post(self, args):
        """Add working space to a building"""
        logger.debug("Handling add working space request")
        working_space = WorkingSpace(building_id=args['building_id'],
                                     name=args['name'],
                                     area=args['area'],
                                     square_meters_per_box=args['square_meters_per_box'],
                                     description=args['description'])

        logger.info(f"Adding espacio de trabajo {working_space}")
        get_session().add(working_space)
        get_session().commit()
        return ok(WorkingSpaceResponse().dump({"data": working_space}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputDeleteWorkingSpace, location='query')
    @bp.response(200, WorkingSpaceIdResponse())
    def delete(self, args):
        """Delete working space from building"""
        working_space_id = args["id"]
        logger.info(f"Deleting espacio de trabajo {working_space_id}")
        delete_instance_by_id(working_space_id, WorkingSpace, "Working Space")
        return ok(WorkingSpaceIdResponse().dump({"data": {"id": working_space_id}}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPutWorkingSpace)
    @bp.response(200, WorkingSpaceResponse())
    def put(self, args):
        """Modify working space details"""
        working_space = get_model_by_id(args["id"], WorkingSpace, "Working Space")
        logger.info(f"Editing working space {working_space}")

        if args.get("area") is not None:
            working_space.area = args["area"]
        if args.get("square_meters_per_box") is not None:
            working_space.square_meters_per_box = args["square_meters_per_box"]
        if args.get("description") is not None:
            working_space.description = args["description"]
        if args.get("name") is not None:
            working_space.name = args["name"]

        get_session().commit()
        return ok(WorkingSpaceResponse().dump({"data": working_space}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
