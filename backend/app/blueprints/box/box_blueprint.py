from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.box.schemas import (
    QueryInputGetBox,
    QueryInputPutBox,
    QueryInputPostBox,
    QueryInputDeleteBox,
    BoxResponse,
    BoxIdResponse,
    BoxResponseWithWorkingSpace,
    BoxSchemaWithWorkingSpace,
    BoxListResponseWithWorkingSpace,
    BoxSchema,
    BoxListResponse,
    QueryInputGetAvailableBoxes
)
from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    delete_instance_by_id,
    search_empty_boxes,
    _get_boxes_with_working_space,
    send_email_to_users_with_box_reservation,
    validate_admin, _box_as_json_with_working_space
)
from app.persistence.models import Box, WorkingSpace
from app.persistence.session import get_session

bp = Blueprint('Box', __name__, description='Operations on box')


@bp.route('/box')
class BoxesAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetBox, location='query')
    @bp.response(200, BoxResponse())
    def get(self, args):
        """Get box by id or all boxes"""
        box_id = args.get("id")

        if box_id is not None:
            box_from_db = get_session().query(
                Box, WorkingSpace
            ).join(
                Box, Box.working_space_id == WorkingSpace.id
            ).filter(
                Box.id == box_id,
            ).one()

            box_with_working_space = _box_as_json_with_working_space(box_from_db)
            logger.info(f"Fetching box con id {box_id}.")
            response_box = BoxResponseWithWorkingSpace().dump(
                {"data": box_with_working_space}
            )
            return ok(response_box)
        else:
            logger.info("Fetching all boxes")
            boxes_from_db = get_session().query(
                Box, WorkingSpace
            ).join(
                Box, Box.working_space_id == WorkingSpace.id
            ).filter(
                Box.deleted_at.is_(None)
            ).all()

            buildings_with_working_space = _get_boxes_with_working_space(boxes_from_db)
            response_boxes = BoxListResponseWithWorkingSpace().dump(
                {"data": BoxSchemaWithWorkingSpace().dump(
                    buildings_with_working_space, many=True
                )}
            )
            return ok(response_boxes)

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPostBox)
    @bp.response(200, BoxResponse())
    def post(self, args):
        """Add new box"""
        logger.debug("Handling add box request")
        box = Box(working_space_id=args['working_space_id'],
                  name=args['name'],
                  description=args['description'])

        logger.info(f"Adding box {box}")
        get_session().add(box)
        get_session().commit()
        return ok(BoxResponse().dump({"data": box}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputDeleteBox, location='query')
    @bp.response(200, BoxIdResponse())
    def delete(self, args):
        """Delete box by id"""
        box_id = args["id"]
        logger.info(f"Deleting box {box_id}")
        delete_instance_by_id(box_id, Box, "Box")
        return ok(BoxIdResponse().dump({"data": {"id": box_id}}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPutBox)
    @bp.response(200, BoxResponse())
    def put(self, args):
        """Modify box details"""
        box = get_model_by_id(args["id"], Box, "Box")
        logger.info(f"Editing box {box}")
        description_before = box.description
        name_before = box.name
        if args.get("description") is not None:
            box.description = args.get("description")
        if args.get("name") is not None:
            box.name = args.get("name")

        get_session().commit()

        send_email_to_users_with_box_reservation(box, name_before, description_before)
        return ok(BoxResponse().dump({"data": box}))


@bp.route("/box/available")
@login_required
@bp.arguments(QueryInputGetAvailableBoxes, location='query')
@bp.response(200, BoxResponse())
def available_boxes(args):
    """Get available boxes for a working_space_id on certain date"""
    working_space_id = args.get("working_space_id")
    the_date = args.get("date")
    boxes = search_empty_boxes(working_space_id, the_date)
    response_working_space = BoxListResponse().dump(
        {"data": BoxSchema().dump(
            boxes, many=True
        )}
    )
    return ok(response_working_space)


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
