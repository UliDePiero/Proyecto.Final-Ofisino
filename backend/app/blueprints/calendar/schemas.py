from marshmallow import Schema, fields, validates, ValidationError, validates_schema
from marshmallow.validate import Length, OneOf

from app.blueprints.helpers import (
    get_model_by_id,
    get_model_by_email,
    custom_error_messages,
    check_start_end,
    check_dates_range_less_than_2_weeks
)
from app.blueprints.meeting_room.schemas import FeaturesSchema, MeetingRoomSchema
from app.persistence.models import MeetingRoom, MeetingRequest, Building


class ParticipantsSchema(Schema):
    name = fields.String(required=True, error_messages=custom_error_messages)
    email = fields.String(required=True, error_messages=custom_error_messages)


class SlotsSchema(Schema):
    timezone = fields.String(required=True, error_messages=custom_error_messages)
    start = fields.String(required=True, error_messages=custom_error_messages)
    end = fields.String(required=True, error_messages=custom_error_messages)


class CalendarsSchema(Schema):
    id = fields.String(required=True, error_messages=custom_error_messages)
    name = fields.String(required=True, error_messages=custom_error_messages)


class AllCalendarsSchema(Schema):
    user = fields.String(required=True, error_messages=custom_error_messages)
    email = fields.String(required=True, error_messages=custom_error_messages)
    cals = fields.List(
        fields.Nested(CalendarsSchema, error_messages=custom_error_messages),
        error_messages=custom_error_messages
    )


class ConferencePropertiesSchema(Schema):
    allowedConferenceSolutionTypes = fields.List(
        fields.String(error_messages=custom_error_messages),
        error_messages=custom_error_messages
    )


class CalendarSchema(Schema):
    id = fields.String(required=True, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(required=True, error_messages=custom_error_messages)
    location = fields.String(required=True, error_messages=custom_error_messages)
    timeZone = fields.String(required=True, error_messages=custom_error_messages)
    conferenceProperties = fields.Nested(ConferencePropertiesSchema, error_messages=custom_error_messages)


class OrganizeMeetingConfirmSchema(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)
    user_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_room_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    date = fields.String(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, error_messages=custom_error_messages)
    description = fields.String(required=False, error_messages=custom_error_messages)


class OrganizeMeetingSchema(Schema):
    emails = fields.List(
        fields.String(required=True, error_messages=custom_error_messages),
        required=True,
        error_messages=custom_error_messages
    )
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    meeting_room_type = fields.String(required=True, error_messages=custom_error_messages)
    meeting_room = fields.Nested(MeetingRoomSchema, required=True, error_messages=custom_error_messages)
    start = fields.String(required=True, error_messages=custom_error_messages)
    end = fields.String(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, error_messages=custom_error_messages)
    kind = fields.String(validate=OneOf(["ok", "missing_features", "conflicts"]))
    missing_features = fields.Nested(FeaturesSchema, required=True, error_messages=custom_error_messages)
    members_conflicts = fields.List(
        fields.Nested(ParticipantsSchema, required=True, error_messages=custom_error_messages),
        required=True,
        error_messages=custom_error_messages
    )


class QueryInputGetSlots(Schema):
    email = fields.String(required=True, error_messages=custom_error_messages)
    cal_id = fields.String(required=True, error_messages=custom_error_messages)
    start = fields.DateTime(required=True, error_messages=custom_error_messages)
    end = fields.DateTime(required=True, error_messages=custom_error_messages)

    @validates_schema
    def _check_email_start_end(self, data, **kwargs):
        get_model_by_email(data['email'])


class QueryInputPostOrganizeMeeting(Schema):
    """meeting_room_type must be 'virtual' or another string representing a physical room"""
    emails = fields.List(
        fields.String(required=True, error_messages=custom_error_messages),
        validate=Length(min=2, error="Se necesitan al menos 2 personas para organizar una reunión."),
        error_messages=custom_error_messages
    )
    start = fields.Date(required=True, error_messages=custom_error_messages)
    end = fields.Date(required=True, error_messages=custom_error_messages)
    time_start = fields.Time(required=True, error_messages=custom_error_messages)
    time_end = fields.Time(required=True, error_messages=custom_error_messages)
    timezone = fields.String(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, strict=True, error_messages=custom_error_messages)
    meeting_room_type = fields.String(required=True, error_messages=custom_error_messages)
    building_id = fields.Int(error_messages=custom_error_messages)
    features = fields.Nested(FeaturesSchema, required=False, error_messages=custom_error_messages)

    @validates_schema
    def check_building_id(self, data, **kwargs):
        if data['meeting_room_type'] != 'virtual':
            if data.get('building_id'):
                get_model_by_id(data['building_id'], Building, "Building")
            else:
                raise ValidationError("Si la reunión no es virtual se necesita especificar el edificio.")

    @validates_schema
    def _check_emails_start_end_duration(self, data, **kwargs):
        check_start_end(data['start'], data['end'], data['time_start'], data['time_end'])
        check_dates_range_less_than_2_weeks(data['start'], data['end'])
        if data['duration'] % 5 != 0:
            raise ValidationError("La duracion no es multiplo de 5.")


class QueryInputPostOrganizeMeetingConfirm(Schema):
    """meeting_room_type must be 'virtual' or another string representing a physical room"""
    emails = fields.List(
        fields.String(required=True, error_messages=custom_error_messages),
        validate=Length(min=2, error="Se necesitan al menos 2 personas para organizar una reunión."),
        error_messages=custom_error_messages
    )
    summary = fields.String(required=False, missing=None, error_messages=custom_error_messages)
    meeting_room_type = fields.String(required=True, error_messages=custom_error_messages)
    meeting_room_id = fields.Int(required=False, missing=None, error_messages=custom_error_messages)
    start = fields.DateTime(required=True, error_messages=custom_error_messages)
    end = fields.DateTime(required=True, error_messages=custom_error_messages)
    description = fields.String(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)
    duration = fields.Int(required=True, strict=True, error_messages=custom_error_messages)
    members_conflicts = fields.List(
        fields.String(required=True, error_messages=custom_error_messages),
        error_messages=custom_error_messages
    )

    @validates("meeting_request_id")
    def check_meeting_request_id(self, meeting_request_id):
        get_model_by_id(meeting_request_id, MeetingRequest, "meeting_request")

    @validates_schema
    def check_meeting_room_id(self, data, **kwargs):
        if data['meeting_room_type'] != 'virtual':
            if data.get('meeting_room_id'):
                get_model_by_id(data['meeting_room_id'], MeetingRoom, "meeting_room")
            else:
                raise ValidationError("Si la reunión no es virtual se necesita especificar la sala.")


class QueryInputPostOrganizeMeetingCancel(Schema):
    meeting_request_id = fields.Int(required=True, error_messages=custom_error_messages)


class QueryInputEmailAccept(Schema):
    member_email = fields.String(required=True, error_messages=custom_error_messages)
    requester = fields.String(required=True, error_messages=custom_error_messages)
    organizer = fields.String(required=True, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)
    description = fields.String(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.String(required=True, error_messages=custom_error_messages)
    meeting_room_id = fields.String(required=True, error_messages=custom_error_messages)
    start = fields.String(required=True, error_messages=custom_error_messages)
    end = fields.String(required=True, error_messages=custom_error_messages)
    events_org = fields.String(required=True, error_messages=custom_error_messages)
    events_mem = fields.String(required=True, error_messages=custom_error_messages)
    event_blocker_id = fields.String(required=True, error_messages=custom_error_messages)


class QueryInputEmailDecline(Schema):
    member = fields.String(required=True, error_messages=custom_error_messages)
    requester = fields.String(required=True, error_messages=custom_error_messages)
    meeting_request_id = fields.String(required=True, error_messages=custom_error_messages)
    summary = fields.String(required=True, error_messages=custom_error_messages)
    start = fields.String(required=True, error_messages=custom_error_messages)
    event_blocker_id = fields.String(required=True, error_messages=custom_error_messages)


class OrganizeMeetingId(Schema):
    id = fields.Int(required=True, error_messages=custom_error_messages)


class SlotsResponse(Schema):
    data = fields.List(fields.Nested(SlotsSchema))


class ParticipantsListResponse(Schema):
    data = fields.List(fields.Nested(ParticipantsSchema))


class CalendarsResponse(Schema):
    data = fields.List(fields.Nested(CalendarsSchema))


class AllCalendarsResponse(Schema):
    data = fields.List(fields.Nested(AllCalendarsSchema))


class CalendarResponse(Schema):
    data = fields.Nested(CalendarSchema)


class OrganizeMeetingListResponse(Schema):
    data = fields.List(fields.Nested(OrganizeMeetingSchema))


class OrganizeMeetingConfirmResponse(Schema):
    data = fields.Nested(OrganizeMeetingConfirmSchema)


class OrganizeMeetingIdResponse(Schema):
    data = fields.Nested(OrganizeMeetingId)
