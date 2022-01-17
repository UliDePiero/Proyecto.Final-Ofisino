from flask import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    get_models_by_user_id,
    status_meeting_request,
    delete_instance_by_id,
    delete_instances_by_id_list,
    get_models_by_id_list
)
from app.blueprints.meeting.meeting_blueprint import MeetingAPI
from app.blueprints.meeting_request.schemas import (
    QueryInputGetMeetingRequest,
    QueryInputDeleteMeetingRequest,
    MeetingRequestResponse,
    MeetingRequestIdResponse,
    MeetingRequestListResponse,
    MeetingRequestSchema,
)
from app.blueprints.meeting_request_user.meeting_request_user_blueprint import MeetingRequestUserAPI
from app.persistence.models import Meeting, User, MeetingRequestUser
from app.persistence.models.meeting_request_model import MeetingRequest
from app.persistence.session import get_session

bp = Blueprint('meeting_request', __name__, description='Operations on meeting request')


@bp.route('/organizemeeting')
class MeetingRequestAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetMeetingRequest, location='query')
    @bp.response(200, MeetingRequestResponse())
    def get(self, args):
        """Get meetings requests by id"""
        meeting_request_id = args.get("id")
        if meeting_request_id is None:
            logger.info("Fetching all meeting requests")
            meeting_request = get_session().query(MeetingRequest).\
                filter(MeetingRequest.deleted_at.is_(None)).all()
            return ok(MeetingRequestListResponse().dump(
                {"data": MeetingRequestSchema().dump(meeting_request, many=True)})
            )
        else:
            logger.info(f"Fetching meeting request with id {meeting_request_id}.")
            meeting_request = get_model_by_id(meeting_request_id, MeetingRequest, "Meeting request")
            return ok(MeetingRequestResponse().dump({"data": meeting_request}))

    @login_required
    @bp.arguments(QueryInputDeleteMeetingRequest, location='query')
    @bp.response(200, MeetingRequestIdResponse())
    def delete(self, args):
        meeting_request_id = args["id"]
        meeting_request = get_model_by_id(meeting_request_id, MeetingRequest, "Meeting request")
        if meeting_request.status == status_meeting_request["pending"]:
            logger.info(f"Cancelling meeting request {meeting_request_id}")
            meeting_request.status = status_meeting_request["cancelled"]
            get_session().commit()
            delete_instance_by_id(meeting_request_id, MeetingRequest, "Meeting Request")
            users = get_session().query(MeetingRequestUser.id).\
                filter_by(meeting_request_id=meeting_request_id).\
                filter(MeetingRequestUser.deleted_at.is_(None)).all()
            id_list = [user.id for user in users]
            delete_instances_by_id_list(id_list, MeetingRequestUser)
        elif meeting_request.status == status_meeting_request["accepted"]:
            meeting_class = MeetingAPI()
            meeting_model = get_session().query(Meeting).filter_by(
                meeting_request_id=meeting_request_id
            ).one_or_none()
            meeting_class.delete_from_db(meeting_id=meeting_model.id)
            logger.info(f"Cancelling meeting request {meeting_request_id}")
            meeting_request.status = status_meeting_request["cancelled"]
            get_session().commit()
            delete_instance_by_id(meeting_request_id, MeetingRequest, "Meeting Request")
            users = get_session().query(MeetingRequestUser.id).\
                filter_by(meeting_request_id=meeting_request_id).\
                filter(MeetingRequestUser.deleted_at.is_(None)).all()
            id_list = [user.id for user in users]
            delete_instances_by_id_list(id_list, MeetingRequestUser)
        return ok(MeetingRequestIdResponse().dump({"data": {"id": meeting_request_id}}))

    def insert_to_db(self, args):
        logger.debug("Handling add meeting_request request")
        meeting_request = MeetingRequest(
            user_id=args['user_id'],
            conditions=args["conditions"],
            status=args["status"]
        )
        logger.info(f"Adding meeting request {meeting_request}")
        get_session().add(meeting_request)
        get_session().commit()
        return MeetingRequestResponse().dump({"data": meeting_request})


@bp.route('/organizemeeting/where-im-member')
@login_required
@bp.response(200, MeetingRequestResponse())
def get():
    """Get meetings requests where the user logged in is member"""
    me: User = current_user
    meeting_request_member_user_id = me.id
    logger.info(
        f"Fetching all meetings requests where user_id {meeting_request_member_user_id}"
        f" is a member"
    )
    meeting_request_user_to_db = {
        "user_id": meeting_request_member_user_id
    }
    m = MeetingRequestUserAPI()
    resp = m.load_from_db(args=meeting_request_user_to_db)
    meeting_request_user_instances = resp['data']
    meeting_request_id_list = [m_r_u['meeting_request_id'] for m_r_u in meeting_request_user_instances]
    meeting_request_list = get_models_by_id_list(meeting_request_id_list, MeetingRequest)
    return ok(MeetingRequestListResponse().dump(
        {"data": MeetingRequestSchema().dump(meeting_request_list, many=True)})
    )


@bp.route('/organizemeeting/by-me')
@login_required
@bp.response(200, MeetingRequestResponse())
def get():
    """Get meetings requests made by the user logged in"""
    me: User = current_user
    meeting_request_request_user_id = me.id
    if me.admin:
        logger.info("Fetching all meeting requests")
        meeting_request = get_session().query(MeetingRequest).\
            filter(MeetingRequest.deleted_at.is_(None)).all()
    else:
        logger.info(
            f"Fetching all meeting requests with user_id {meeting_request_request_user_id}"
        )
        meeting_request = get_models_by_user_id(
            meeting_request_request_user_id,
            MeetingRequest,
            "Meeting request"
        )
    return ok(MeetingRequestListResponse().dump(
        {"data": MeetingRequestSchema().dump(meeting_request, many=True)})
    )


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
