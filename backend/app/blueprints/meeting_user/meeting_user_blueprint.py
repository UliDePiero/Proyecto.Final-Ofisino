from flask import jsonify
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.helpers import ok, get_model_by_id, delete_instance_by_id, get_models_by_user_id
from app.blueprints.meeting_user.schemas import (
    MeetingUserResponse,
    MeetingUserIdResponse,
    MeetingUserListResponse,
    MeetingUserSchema,
)
from app.persistence.models.meeting_user_model import MeetingUser
from app.persistence.session import get_session

bp = Blueprint('meeting_user', __name__, description='Operations on meeting user')


class MeetingUserAPI:

    def load_from_db(self, args):
        meeting_user_id = args.get("id")
        meeting_user_user_id = args.get("user_id")
        if meeting_user_id is None:
            if meeting_user_user_id is None:
                logger.info("Fetching all meeting users")
                meeting_user = get_session().query(MeetingUser).filter(MeetingUser.deleted_at.is_(None)).all()
                return (MeetingUserListResponse().dump(
                    {"data": MeetingUserSchema().dump(meeting_user, many=True)})
                )
            else:
                logger.info(f"Fetching all meeting users with user_id {meeting_user_user_id}")
                meeting_request_user = get_models_by_user_id(
                    meeting_user_user_id,
                    MeetingUser,
                    "Meeting user"
                )
                return (MeetingUserListResponse().dump(
                    {"data": MeetingUserSchema().dump(meeting_request_user, many=True)})
                )
        else:
            logger.info(f"Fetching meeting user with id {meeting_user_id}.")
            meeting_user = get_model_by_id(meeting_user_id, MeetingUser, "Meeting request")
            return MeetingUserResponse().dump({"data": meeting_user})

    def insert_to_db(self, args):
        logger.debug("Handling add meeting_users request")
        meeting_users = [
            MeetingUser(
                meeting_id=user['meeting_id'],
                user_id=user["user_id"]
            )
            for user in args
        ]
        logger.info(f"Adding meeting users {meeting_users}")
        get_session().add_all(meeting_users)
        get_session().commit()
        return (MeetingUserListResponse().dump(
            {"data": MeetingUserSchema().dump(meeting_users, many=True)})
        )

    def delete(self, args):
        meeting_user_id = args["id"]
        logger.info(f"Deleting meeting user {meeting_user_id}")

        delete_instance_by_id(meeting_user_id, MeetingUser, "Meeting User")
        return ok(MeetingUserIdResponse().dump({"data": {"id": meeting_user_id}}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
