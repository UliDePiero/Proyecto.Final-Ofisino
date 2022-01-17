from flask import jsonify
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import ok, get_model_by_id, delete_instance_by_id, get_models_by_user_id
from app.blueprints.meeting_request_user.schemas import (
    MeetingRequestUserResponse,
    MeetingRequestUserIdResponse,
    MeetingRequestUserListResponse,
    MeetingRequestUserSchema,
)
from app.persistence.models.meeting_request_user_model import MeetingRequestUser
from app.persistence.session import get_session

bp = Blueprint('meeting_request_user', __name__, description='Operations on meeting request user')


class MeetingRequestUserAPI:

    def load_from_db(self, args):
        meeting_request_user_id = args.get("id")
        meeting_request_user_user_id = args.get("user_id")
        if meeting_request_user_id is None:
            if meeting_request_user_user_id is None:
                logger.info("Fetching all meeting request users")
                meeting_request_user = get_session().query(MeetingRequestUser).\
                    filter(MeetingRequestUser.deleted_at.is_(None)).all()
                return (MeetingRequestUserListResponse().dump(
                    {"data": MeetingRequestUserSchema().dump(meeting_request_user, many=True)})
                )
            else:
                logger.info(f"Fetching all meeting request users with user_id {meeting_request_user_user_id}")
                meeting_request_user = get_models_by_user_id(
                    meeting_request_user_user_id,
                    MeetingRequestUser,
                    "Meeting request user"
                )
                return (MeetingRequestUserListResponse().dump(
                    {"data": MeetingRequestUserSchema().dump(meeting_request_user, many=True)})
                )
        else:
            logger.info(f"Fetching meeting request user with id {meeting_request_user_id}.")
            meeting_request_user = get_model_by_id(
                meeting_request_user_id,
                MeetingRequestUser,
                "Meeting request user"
            )
            return MeetingRequestUserResponse().dump({"data": meeting_request_user})

    def insert_to_db(self, args):
        logger.debug("Handling add meeting_request_users request")
        meeting_request_users = [
            MeetingRequestUser(
                meeting_request_id=user['meeting_request_id'],
                user_id=user["user_id"]
            )
            for user in args
        ]
        logger.info(f"Adding meeting request users {meeting_request_users}")
        get_session().add_all(meeting_request_users)
        get_session().commit()
        return (MeetingRequestUserListResponse().dump(
            {"data": MeetingRequestUserSchema().dump(meeting_request_users, many=True)})
        )

    def delete(self, args):
        meeting_request_user_id = args["id"]
        logger.info(f"Deleting meeting request user {meeting_request_user_id}")

        delete_instance_by_id(meeting_request_user_id, MeetingRequestUser, "Meeting Request User")
        return ok(MeetingRequestUserIdResponse().dump({"data": {"id": meeting_request_user_id}}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
