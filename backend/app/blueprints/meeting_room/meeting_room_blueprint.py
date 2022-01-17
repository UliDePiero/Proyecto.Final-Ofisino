from flask import jsonify
from flask.views import MethodView
from flask_login import login_required
from flask_smorest import Blueprint
from loguru import logger

from app.blueprints.api_extra_functions import create_calendar
from app.blueprints.helpers import (
    ok,
    get_model_by_id,
    delete_instance_by_id,
    send_email_to_users_with_meeting_room_meetings,
    validate_admin
)
from app.blueprints.meeting_room.schemas import (
    QueryInputGetMeetingRoom,
    QueryInputPutMeetingRoom,
    QueryInputPostMeetingRoom,
    QueryInputDeleteMeetingRoom,
    MeetingRoomResponse,
    MeetingRoomIdResponse,
    MeetingRoomListResponseWithBuilding,
    MeetingRoomSchemaWithBuilding,
    MeetingRoomResponseWithBuilding
)
from app.calendar_class import DOMAIN
from app.persistence.models import Building
from app.persistence.models.meeting_room_model import MeetingRoom
from app.persistence.session import get_session

bp = Blueprint('meeting_room', __name__, description='Operations on meeting room')


@bp.route('/meetingroom')
class MeetingRoomAPI(MethodView):

    @login_required
    @bp.arguments(QueryInputGetMeetingRoom, location='query')
    @bp.response(200, MeetingRoomResponse())
    def get(self, args):
        meeting_room_id = args.get("id")
        if meeting_room_id is None:
            logger.info("Fetching all salas de reunion")
            meetings_room_from_db = get_session().query(
                MeetingRoom, Building
            ).join(
                MeetingRoom, MeetingRoom.building_id == Building.id
            ).filter(
                MeetingRoom.deleted_at.is_(None)
            ).all()
            meetings_room_with_building = self._get_meetings_room_with_building(meetings_room_from_db)
            response_building = MeetingRoomListResponseWithBuilding().dump(
                {"data": MeetingRoomSchemaWithBuilding().dump(
                    meetings_room_with_building, many=True
                )}
            )
            return ok(response_building)
        else:
            meetings_room_from_db = get_session().query(
                MeetingRoom, Building
            ).join(
                MeetingRoom, MeetingRoom.building_id == Building.id
            ).filter(
                MeetingRoom.id == meeting_room_id
            ).one()
            meeting_room_with_building = self._meeting_room_as_json(meetings_room_from_db)
            logger.info(f"Fetching meeting room con id {meeting_room_id}.")
            response_meeting_room = MeetingRoomResponseWithBuilding().\
                dump({"data": meeting_room_with_building})
            return ok(response_meeting_room)

    def _get_meetings_room_with_building(self, meetings_room):
        return [self._meeting_room_as_json(meeting_room)
                for meeting_room in meetings_room]

    def _meeting_room_as_json(self, meeting_room):
        return {
            'id': meeting_room.MeetingRoom.id,
            'features': meeting_room.MeetingRoom.features,
            'capacity': meeting_room.MeetingRoom.capacity,
            'name': meeting_room.MeetingRoom.name,
            'description': meeting_room.MeetingRoom.description,
            'building': meeting_room.Building.to_dict(),
            'calendar': meeting_room.MeetingRoom.calendar
        }

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPostMeetingRoom)
    @bp.response(200, MeetingRoomResponse())
    def post(self, args):
        logger.debug("Handling add meeting room request")
        calendar_id = create_calendar(calendar_summary=args['name'])
        if not calendar_id:
            return jsonify({"errors": {"json": {"name": "Ya existe una sala de reunion con ese nombre o "
                                                        f"hubo un problema con el servicio de {DOMAIN}."}}}
                           ), 400
        meeting_room = MeetingRoom(name=args['name'],
                                   capacity=args['capacity'],
                                   building_id=args['building_id'],
                                   features=args['features'],
                                   description=args['description'],
                                   calendar=calendar_id)

        logger.info(f"Adding sala de reunion {meeting_room}")
        get_session().add(meeting_room)
        get_session().commit()
        return ok(MeetingRoomResponse().dump({"data": meeting_room}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputDeleteMeetingRoom, location='query')
    @bp.response(200, MeetingRoomIdResponse())
    def delete(self, args):
        meeting_room_id = args["id"]
        logger.info(f"Deleting meeting room {meeting_room_id}")

        delete_instance_by_id(meeting_room_id, MeetingRoom, "Meeting Room")
        return ok(MeetingRoomIdResponse().dump({"data": {"id": meeting_room_id}}))

    @login_required
    @validate_admin
    @bp.arguments(QueryInputPutMeetingRoom)
    @bp.response(200, MeetingRoomResponse())
    def put(self, args):
        meeting_room = get_model_by_id(args['id'], MeetingRoom, "Sala de Reunion")
        logger.info(f"Editing sala de reunion {meeting_room}")

        older_meeting_room = MeetingRoom(name=meeting_room.name,
                                         capacity=meeting_room.capacity,
                                         building_id=meeting_room.building_id,
                                         features=meeting_room.features,
                                         description=meeting_room.description,
                                         calendar=meeting_room.calendar)
        if args.get("capacity") is not None:
            meeting_room.capacity = args['capacity']
        if args.get("features") is not None:
            meeting_room.features = args['features']
        if args.get("description") is not None:
            meeting_room.description = args['description']
        if args.get("name") is not None:
            meeting_room.name = args['name']

        meeting_room = MeetingRoom(id=meeting_room.id,
                                   capacity=meeting_room.capacity,
                                   features=meeting_room.features,
                                   building_id=meeting_room.building_id,
                                   name=meeting_room.name,
                                   description=meeting_room.description,
                                   calendar=meeting_room.calendar)
        get_session().commit()
        send_email_to_users_with_meeting_room_meetings(meeting_room, older_meeting_room)
        return ok(MeetingRoomResponse().dump({"data": meeting_room}))


@bp.errorhandler(422)
@bp.errorhandler(400)
def handle_error(err):
    headers = err.data.get("headers", None)
    messages = err.data.get("messages", ["Invalid request."])
    if headers:
        return jsonify({"errors": messages}), err.code, headers
    else:
        return jsonify({"errors": messages}), err.code
