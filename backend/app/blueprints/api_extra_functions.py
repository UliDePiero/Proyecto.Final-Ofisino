from loguru import logger

from app.api_credentials import get_service_credentials_or_abort_with_http_500
from app.blueprints.helpers import get_model_by_id
from app.calendar_class import CalendarManager
from app.persistence.models import Box


def create_calendar(calendar_summary):
    logger.info(f"Getting API client")
    cred = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=cred)
    logger.info("Creating calendar via API")
    new_calendar_id = cman.create_calendar(calendar_summary)
    return new_calendar_id


def create_all_date_event(email, box_id, start, end):
    service_credentials = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=service_credentials)
    box = get_model_by_id(box_id, Box, "Box")
    return cman.create_all_date_event(
        email=email,
        calendar_id=email,
        event_summary=f'Reserva de Box "{box.name}"',
        event_start=start.isoformat(),
        event_end=end.isoformat()
    )


def delete_event(email, event_id):
    cred = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=cred)
    cman.delete_event_for_all_users(email, event_id)


def get_event_meet_url_from_api(email, event_id):
    cred = get_service_credentials_or_abort_with_http_500()
    cman = CalendarManager(config=cred)
    return cman.get_event_meet_url(email, event_id)
