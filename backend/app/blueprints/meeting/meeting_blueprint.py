import datetime

from flask import jsonify
from flask.views import MethodView
from flask_login import current_user, login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.api_extra_functions import delete_event, get_event_meet_url_from_api
from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    delete_instance_by_id,
    get_models_by_user_id,
    delete_instances_by_id_list,
    get_models_by_id_list
)
from app.blueprints.meeting.schemas import (
    QueryInputGetMeeting,
    MeetingResponse,
    MeetingListResponse,
    MeetingSchema,
    MeetingResponseWithMeetingRoomAndUser,
)
from app.blueprints.meeting_user.meeting_user_blueprint import MeetingUserAPI
from app.persistence.models import User, MeetingUser, MeetingRoom
from app.persistence.models.meeting_model import Meeting
from app.persistence.session import get_session

bp = Blueprint('meeting', __name__, description='Operations on meeting')


@bp.route('/meeting')
class MeetingAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetMeeting, location='query')
    @bp.response(200, MeetingResponse())
    def get(self, args):
        """Get meetings by id or meeting_request id"""
        meeting_id = args.get("id")
        meeting_request_id = args.get("meeting_request_id")
        if meeting_id is None and meeting_request_id is None:
            logger.info("Fetching all meetings")
            meeting = get_session().query(Meeting).filter(Meeting.deleted_at.is_(None)).all()
            return ok(MeetingListResponse().dump(
                {"data": MeetingSchema().dump(meeting, many=True)})
            )
        else:
            if meeting_request_id:
                logger.info(f"Fetching meeting with meeting_request_id {meeting_request_id}.")
                meeting = get_session().query(Meeting).filter_by(meeting_request_id=meeting_request_id).\
                    filter(Meeting.deleted_at.is_(None)).one_or_none()
                meeting_id = meeting.id
            else:
                logger.info(f"Fetching meeting with id {meeting_id}.")
                meeting = get_model_by_id(meeting_id, Meeting, "Meeting")

            if meeting.meeting_room_id:
                meetings_from_db = get_session().query(
                    Meeting, MeetingRoom, User
                ).filter(
                    Meeting.id == meeting_id,
                    Meeting.meeting_room_id == MeetingRoom.id,
                    Meeting.user_id == User.id
                ).one()
            else:
                meetings_from_db = get_session().query(
                    Meeting, User
                ).join(
                    Meeting, Meeting.user_id == User.id
                ).filter(
                    Meeting.id == meeting_id
                ).one()

            meeting_with_meeting_room_and_user = self._meeting_as_json(
                meetings_from_db, meeting.meeting_room_id
            )
            response_meeting = MeetingResponseWithMeetingRoomAndUser().\
                dump({"data": meeting_with_meeting_room_and_user})
            return ok(response_meeting)

    def _meeting_as_json(self, meeting, meeting_room):
        meeting_json = {
            'id': meeting.Meeting.id,
            'requester_user': meeting.User.to_dict(),
            'date_start': meeting.Meeting.date,
            'date_end': (
                    datetime.datetime.fromisoformat(meeting.Meeting.date)
                    + datetime.timedelta(minutes=meeting.Meeting.duration)
            ).isoformat(),
            'description': meeting.Meeting.description,
            'summary': meeting.Meeting.summary
        }
        users = get_session().query(MeetingUser).filter_by(meeting_id=meeting.Meeting.id).\
            filter(MeetingUser.deleted_at.is_(None)).all()
        meeting_json['attendees'] = [
            get_model_by_id(user.user_id, User, "User").to_dict()
            for user in users
        ]
        if meeting_room:
            meeting_json['meeting_room'] = meeting.MeetingRoom.to_dict()
        user_email = get_model_by_id(users[0].user_id, User, "User").email
        meeting_event = get_event_meet_url_from_api(user_email, meeting.Meeting.event)
        meeting_json['event'] = meeting_event
        return meeting_json

    def insert_to_db(self, args):
        logger.debug("Handling add meeting request")
        meeting = Meeting(
            user_id=args['user_id'],
            meeting_room_id=args['meeting_room_id'],
            meeting_request_id=args['meeting_request_id'],
            date=args['date'],
            duration=args['duration'],
            description=args['description'],
            summary=args['summary'],
            event=args['event']
        )
        logger.info(f"Adding meeting {meeting}")
        get_session().add(meeting)
        get_session().commit()
        return MeetingResponse().dump({"data": meeting})

    def delete_from_db(self, meeting_id):
        logger.info(f"Deleting meeting {meeting_id}")
        meeting = get_model_by_id(meeting_id, Meeting, "Meeting")
        users = get_session().query(MeetingUser).filter_by(meeting_id=meeting.id).all()
        user_email = get_model_by_id(users[0].user_id, User, "User").email
        delete_event(user_email, meeting.event)
        delete_instance_by_id(meeting_id, Meeting, "Meeting")
        id_list = [user.id for user in users]
        delete_instances_by_id_list(id_list, MeetingUser)
        return


@bp.route('/meeting/where-im-member')
@login_required
@bp.response(200, MeetingResponse())
def get():
    """Get meetings where the user logged in is member"""
    me: User = current_user
    meeting_member_user_id = me.id
    logger.info(
        f"Fetching all meetings where user_id {meeting_member_user_id}"
        f" is a member"
    )
    meeting_user_to_db = {
        "user_id": meeting_member_user_id
    }
    m = MeetingUserAPI()
    resp = m.load_from_db(args=meeting_user_to_db)
    meeting_user_instances = resp['data']
    meeting_id_list = [meeting_user['meeting_id'] for meeting_user in meeting_user_instances]
    meeting_list = get_models_by_id_list(meeting_id_list, Meeting)
    return ok(MeetingListResponse().dump(
        {"data": MeetingSchema().dump(meeting_list, many=True)})
    )


@bp.route('/meeting/by-me')
@login_required
@bp.response(200, MeetingResponse())
def get():
    """Get meetings made by the user logged in"""
    me: User = current_user
    meeting_request_user_id = me.id
    logger.info(
        f"Fetching all meetings with user_id {meeting_request_user_id}"
    )
    meeting = get_models_by_user_id(
        meeting_request_user_id,
        Meeting,
        "Meeting"
    )
    return ok(MeetingListResponse().dump(
        {"data": MeetingSchema().dump(meeting, many=True)})
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
