import dataclasses
import datetime
import datetime as dt
import os
from typing import Optional
from uuid import uuid4

import pandas as pd
import pytz
import requests
from dateutil.parser import parse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

DOMAIN_ADMIN_ACC = os.environ.get('DOMAIN_ADMIN_ACC')
DOMAIN = os.environ.get('DOMAIN')


@dataclasses.dataclass
class BusySlot:
    start: datetime.datetime
    end: datetime.datetime

    def to_dict(self):
        busy_slot_dict = {
            "start": self.start.isoformat(),
            "end": self.end.isoformat()
        }
        return busy_slot_dict


@dataclasses.dataclass
class FreeSlot:
    start: dt.datetime
    end: dt.datetime

    def to_dict(self):
        busy_slot_dict = {
            "start": self.start.isoformat(),
            "end": self.end.isoformat()
        }
        return busy_slot_dict


@dataclasses.dataclass
class MeetingSlot:
    start: dt.datetime
    end: dt.datetime

    def to_dict(self):
        meeting_slot_dict = {
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
        }
        return meeting_slot_dict


@dataclasses.dataclass
class CalendarAllDateEvent:
    summary: str
    start: str
    end: str
    timezone: str

    def to_dict(self):
        event_dict = {
            "summary": self.summary,
            "transparency": "transparent",
            "start": {
                'date': self.start,
                'timeZone': self.timezone
            },
            "end": {
                'date': self.end,
                'timeZone': self.timezone
            }
        }
        return event_dict


@dataclasses.dataclass
class CalendarEvent:
    summary: str
    start: str
    end: str
    timezone: str
    description: str
    attendees: list[str]

    def to_dict(self):
        event_dict = {
            "summary": self.summary,
            "start": {
                'dateTime': self.start,
                'timeZone': self.timezone
            },
            "end": {
                'dateTime': self.end,
                'timeZone': self.timezone
            },
            "description": self.description,
            "conferenceData": {
                "createRequest": {
                    "requestId": f"{uuid4().hex}",
                    "conferenceSolutionKey": {
                        "type": "hangoutsMeet"
                    }
                }
            },
            "attendees": [
                {
                    'email': att
                }
                for att in self.attendees
            ]
        }
        return event_dict


class CalendarManager:
    BS_AS_TIMEZONE = 'America/Argentina/Buenos_Aires'

    def __init__(self, config):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            self.cred = config
        elif DOMAIN.casefold() == "OFFICE".casefold():
            self.token = config

    def get_users(self):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            return self.get_users_google()
        elif DOMAIN.casefold() == "OFFICE".casefold():
            return self.get_users_office()

    def get_users_google(self):
        cred = self.cred.with_subject(DOMAIN_ADMIN_ACC)
        service = build('admin', 'directory_v1', credentials=cred)
        request = service.users().list(customer='my_customer', maxResults=500, orderBy='email')
        response = request.execute()
        users = response.get('users', [])
        while request:
            request = service.users().list_next(previous_request=request, previous_response=response)
            if request:
                response = request.execute()
                users.extend(response.get('users', []))
        return users

    def get_users_office(self):
        return [
            {
                'name': {
                    'fullName': u['displayName']
                },
                'primaryEmail': u['userPrincipalName']
            }
            for u in self._get_office('/users').get('value', [])
        ]

    def create_calendar(self, calendar_summary):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            return self.create_calendar_google(calendar_summary)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            calendar_name = f"{calendar_summary}_{int(datetime.datetime.utcnow().timestamp())}"
            return self.create_calendar_office(calendar_name)

    def create_calendar_google(self, calendar_summary):
        calendar = {
            'summary': calendar_summary,
            'timeZone': os.environ.get('SERVER_TIMEZONE') or "America/Argentina/Buenos_Aires"
        }
        cred = self.cred.with_subject(DOMAIN_ADMIN_ACC)
        api_service = build('calendar', 'v3', credentials=cred)
        created_calendar = api_service.calendars().insert(body=calendar).execute()
        return created_calendar.get('id')

    def create_calendar_office(self, calendar_summary):
        if self._get_calendar_id_by_name_office(DOMAIN_ADMIN_ACC, calendar_summary):
            return None

        return requests.post(
            f'https://graph.microsoft.com/v1.0/users/{DOMAIN_ADMIN_ACC}/calendars',
            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            json={
                "name": calendar_summary
            }
        ).json().get('id')

    def _get_calendar_id_by_name_office(self, email, calendar_name):
        user_calendars = self._get_user_calendars_office(email)
        for calendar in user_calendars['value']:
            if calendar['name'] == calendar_name:
                return calendar['id']

    def _get_user_default_calendar_office(self, user):
        return self._get_office(f'/users/{user}/calendar')

    def _get_user_calendars_office(self, user_id):
        return self._get_office(f'/users/{user_id}/calendars')

    def _get_office(self, endpoint, **kwargs):
        return requests.get(
            f'https://graph.microsoft.com/v1.0/{endpoint}',
            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            **kwargs
        ).json()

    def create_event(self, email, calendar_id,
                     event_summary, event_start, event_end, event_description, event_attendees,
                     meeting_room_type, meeting_room_calendar_id
                     ):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            if meeting_room_calendar_id:
                event_attendees.append(meeting_room_calendar_id)
            return self.create_event_google(email, calendar_id,
                                            event_summary, event_start, event_end,
                                            event_description, event_attendees,
                                            meeting_room_type)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            return self.create_event_office(email, meeting_room_calendar_id,
                                            event_summary, event_start, event_end,
                                            event_description, event_attendees,
                                            meeting_room_type)

    def create_event_google(self, email, calendar_id,
                            event_summary, event_start, event_end, event_description, event_attendees,
                            meeting_room_type
                            ):
        event = CalendarEvent(
            summary=event_summary,
            start=event_start,
            end=event_end,
            timezone=self._get_timezone_from_datetime(event_start),
            description=event_description,
            attendees=event_attendees
        ).to_dict()
        if meeting_room_type == 'placeholder':
            conference_data_version = 0
        else:
            conference_data_version = 1
        cred = self.cred.with_subject(email)
        api_service = build('calendar', 'v3', credentials=cred)
        created_event = api_service.events().insert(calendarId=calendar_id,
                                                    body=event,
                                                    sendUpdates='all',
                                                    conferenceDataVersion=conference_data_version
                                                    ).execute()
        return created_event.get('id')

    def _get_timezone_from_datetime(self, date_time: str):
        tz_string = datetime.datetime.fromisoformat(date_time).strftime('%Z')
        hour = tz_string.split('C')[1]
        if hour:
            h, m = hour.split(':')
        else:
            h = 0
            m = 0

        tz_offset = int(h) * 3600 + int(m) * 60
        timezones = pytz.common_timezones
        offset_days, offset_seconds = 0, int(tz_offset)
        if offset_seconds < 0:
            offset_days = -1
            offset_seconds += 24 * 3600
        desired_delta = datetime.timedelta(offset_days, offset_seconds)
        null_delta = datetime.timedelta(0, 0)
        for tz_name in timezones:
            tz = pytz.timezone(tz_name)
            non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
            if desired_delta == non_dst_offset[0]:
                return tz_name
        return "Pacific Standard Time"

    def create_event_office(self, email, meeting_room_calendar_id,
                            event_summary, event_start, event_end, event_description, event_attendees,
                            meeting_room_type
                            ):
        if meeting_room_calendar_id:
            user = DOMAIN_ADMIN_ACC
            calendar_id = meeting_room_calendar_id
        else:
            user = email
            calendar_id = self._get_user_default_calendar_office(email).get('id')
        resp = self._get_office(f"/users?$filter=userPrincipalName in {tuple(event_attendees)}")
        event_attendees = [
            {
                "emailAddress": {
                    "address": attendee['userPrincipalName'],
                    "name": attendee['displayName']
                },
                "type": "required"
            }
            for attendee in resp.get('value', [])
        ]
        if meeting_room_type == 'placeholder':
            online_meeting = False
        else:
            online_meeting = True
        return requests.post(
            f'https://graph.microsoft.com/v1.0/users/{user}/calendars/{calendar_id}/events',

            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            json={
                "subject": event_summary,
                "body": {"contentType": "HTML", "content": event_description},
                "start": {
                    "dateTime": event_start,
                    "timeZone": self._get_timezone_from_datetime(event_start)
                },
                "end": {
                    "dateTime": event_end,
                    "timeZone": self._get_timezone_from_datetime(event_end)
                },
                "location": {
                    "displayName": "Ofisino Headquarters"
                },
                "attendees": event_attendees,
                "allowNewTimeProposals": False,
                "responseRequested": True,
                "isOnlineMeeting": online_meeting
            }
        ).json().get('iCalUId')

    def create_all_date_event(self, email, calendar_id, event_summary, event_start, event_end):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            return self.create_all_date_event_google(
                email, calendar_id, event_summary, event_start, event_end
            )
        elif DOMAIN.casefold() == "OFFICE".casefold():
            return self.create_all_date_event_office(
                email, event_summary, event_start, event_end
            )

    def create_all_date_event_google(self, email, calendar_id, event_summary, event_start, event_end):
        event = CalendarAllDateEvent(
            summary=event_summary,
            start=event_start,
            end=event_end,
            timezone=os.environ.get('SERVER_TIMEZONE') or "America/Argentina/Buenos_Aires"
        ).to_dict()
        cred = self.cred.with_subject(email)
        api_service = build('calendar', 'v3', credentials=cred)
        created_event = api_service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event.get('id')

    def create_all_date_event_office(self, email, event_summary, event_start, event_end):
        event_start = f"{event_start}T00:00"
        event_end = (f"{(datetime.date.fromisoformat(event_end) + datetime.timedelta(days=1)).isoformat()}"
                     f"T00:00")
        return requests.post(
            f'https://graph.microsoft.com/v1.0/users/{email}/calendar/events',

            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            json={
                "subject": event_summary,
                "start": {
                    "dateTime": event_start,
                    "timeZone": os.environ.get('SERVER_TIMEZONE') or "America/Argentina/Buenos_Aires"
                },
                "end": {
                    "dateTime": event_end,
                    "timeZone": os.environ.get('SERVER_TIMEZONE') or "America/Argentina/Buenos_Aires"
                },
                "location": {
                    "displayName": "Ofisino Headquarters"
                },
                "allowNewTimeProposals": False,
                "showAs": "free",
                "isAllDay": True
            }
        ).json().get('iCalUId')

    def get_event_meet_url(self, email, event_id):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            event = self.get_event_google(email, event_id)
            if event:
                return event.get('hangoutLink')
        elif DOMAIN.casefold() == "OFFICE".casefold():
            event = self._get_event_by_iCalUId(email, event_id)
            if event:
                event_with_meet = event.get('onlineMeeting')
                if event_with_meet:
                    return event_with_meet.get('joinUrl')

    def get_event_google(self, email, event_id):
        try:
            cred = self.cred.with_subject(email)
            api_service = build('calendar', 'v3', credentials=cred)
            return api_service.events().get(calendarId=email, eventId=event_id).execute()
        except HttpError as err:
            if err.resp.status == 404:
                return None
            else:
                raise

    def get_events_between_time(self, email, start, end):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            return self.get_events_between_time_google(email, start, end)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            return self.get_events_between_time_office(email, start, end)

    def get_events_between_time_office(self, email, start, end):
        start_no_tz = datetime.datetime.fromisoformat(start).replace(tzinfo=None).isoformat()
        end_no_tz = datetime.datetime.fromisoformat(end).replace(tzinfo=None).isoformat()
        endpoint = (f"/users/{email}/calendar/events?"
                    f"$filter=((start/dateTime le '{start_no_tz}'and end/dateTime ge '{end_no_tz}') "
                    f"or (start/dateTime ge '{start_no_tz}'and start/dateTime le '{end_no_tz}') "
                    f"or (end/dateTime ge '{start_no_tz}'and end/dateTime le '{end_no_tz}')) "
                    f"and showAs ne 'free'")
        resp = requests.get(
            f'https://graph.microsoft.com/v1.0/{endpoint}',
            headers={'Authorization': f'Bearer {self.token["access_token"]}',
                     'Prefer': f'outlook.timezone = "{self._get_timezone_from_datetime(start)}"'}
        ).json().get('value', [])

        return[
            {
                'id': e['iCalUId'],
                'organizer':
                    {
                        'email': e.get('organizer')['emailAddress']['address']
                    },
                'summary': e.get('subject'),
                'htmlLink': e.get('webLink')
            }
            for e in resp
        ]

    def get_events_between_time_google(self, email, start, end):
        events_list = []
        page_token = None
        sync_token = None
        cred = self.cred.with_subject(email)
        api_service = build('calendar', 'v3', credentials=cred)
        while not sync_token:
            events = api_service.events().list(
                calendarId=email,
                pageToken=page_token,
                timeMin=start,
                timeMax=end
            ).execute()
            for event in events['items']:
                if event.get('transparency') != 'transparent':
                    events_list.append(event)
            page_token = events.get('nextPageToken')
            sync_token = events.get('nextSyncToken')
        return events_list

    def delete_event_for_all_users(self, email, event_id):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            self.delete_event_for_all_users_google(email, event_id)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            self.delete_event_for_all_users_office(email, event_id)

    def delete_event_for_all_users_google(self, email, event_id):
        try:
            cred = self.cred.with_subject(email)
            api_service = build('calendar', 'v3', credentials=cred)
            event = api_service.events().get(calendarId=email, eventId=event_id).execute()
            cred_2 = self.cred.with_subject(event['organizer']['email'])
            api_service_2 = build('calendar', 'v3', credentials=cred_2)
            api_service_2.events().delete(calendarId=event['organizer']['email'],
                                          eventId=event_id,
                                          sendUpdates='all').execute()
        except HttpError as err:
            if err.resp.status == 404:
                return
            else:
                raise

    def delete_event_for_all_users_office(self, email, iCalUId):
        attendee_calendar_event = self._get_event_by_iCalUId(email, iCalUId)
        if attendee_calendar_event:
            organizador = attendee_calendar_event.get('organizer')['emailAddress']['address']
            organizer_calendar_event = self._get_event_by_iCalUId(organizador, iCalUId)
            if organizer_calendar_event:
                self._delete_office(f"/users/{organizador}/events/{organizer_calendar_event.get('id')}")

    def delete_event(self, email, event_id, send_updates: bool = True):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            self.delete_event_google(email, event_id, send_updates)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            self.delete_event_office(email, event_id)

    def delete_event_google(self, email, event_id, send_updates: bool = True):
        try:
            cred = self.cred.with_subject(email)
            api_service = build('calendar', 'v3', credentials=cred)
            if send_updates:
                send = 'all'
            else:
                send = 'none'
            api_service.events().delete(calendarId=email, eventId=event_id, sendUpdates=send).execute()
        except HttpError as err:
            if err.resp.status == 404:
                return
            else:
                raise

    def delete_event_office(self, email, iCalUId):
        event = self._get_event_by_iCalUId(email, iCalUId)
        if event:
            if event.get('organizer')['emailAddress']['address'] != email:
                requests.post(
                    f"https://graph.microsoft.com/v1.0/users/{email}/events/{event.get('id')}/decline",
                    headers={'Authorization': f'Bearer {self.token["access_token"]}'}
                )
            else:
                self._delete_office(f"/users/{email}/events/{event.get('id')}")

    def _delete_office(self, endpoint, **kwargs):
        return requests.delete(
            f'https://graph.microsoft.com/v1.0/{endpoint}',
            headers={'Authorization': f'Bearer {self.token["access_token"]}'},
            **kwargs
        )

    def _get_event_by_iCalUId(self, email, iCalUId):
        """If email is DOMAIN_ADMIN_ACC it must search on all of its calendars
        otherwise it searches on the default calendar"""
        if email != DOMAIN_ADMIN_ACC:
            ev = self._get_office(f"/users/{email}/events?$filter=iCalUId eq '{iCalUId}'").get('value')
            if ev:
                return ev[0]
        quantity = self._get_office(f"/users/{email}/calendars/$count")
        id_list = self._get_office(f"/users/{email}/calendars?$select=id && top={quantity}").get('value', [])
        for cal in id_list:
            event = self._get_office(
                f"/users/{email}/calendars/{cal['id']}/events?select=iCalUId"
            ).get('value', [])
            for ev in event:
                if ev['iCalUId'] == iCalUId:
                    return self._get_office(f"/users/{email}/calendars/{cal['id']}/events/{ev['id']}")

    def get_all_users_calendars(self) -> list[dict]:
        pass  # ToDo

    def get_all_users_calendars_office(self) -> list[dict]:
        pass  # ToDo

    def get_all_users_calendars_google(self) -> list[dict]:
        list_user_cals = []
        users = self.get_users()
        for user in users:
            cals = self.get_calendars(user['primaryEmail'])
            user_cals_dict = {
                "user": user['name']['fullName'],
                "email": user['primaryEmail'],
                "cals": cals,
            }
            list_user_cals.append(user_cals_dict)
        return list_user_cals

    def get_calendars(self, email) -> list[dict]:
        pass  # ToDo

    def get_calendars_office(self, email) -> list[dict]:
        pass  # ToDo

    def get_calendars_google(self, email) -> list[dict]:
        cred = self.cred.with_subject(email)
        api_service = build('calendar', 'v3', credentials=cred)
        resp = api_service.calendarList().list().execute()

        calendars = resp['items']
        return [
            {
                'id': cal['id'],
                'name': cal['summary']
            }
            for cal in calendars
        ]

    def get_calendar_by_id(self, email, calendar_id):
        pass  # ToDo

    def get_calendar_by_id_office(self, email, calendar_id):
        pass  # ToDo

    def get_calendar_by_id_google(self, email, calendar_id):
        try:
            cred = self.cred.with_subject(email)
            api_service = build('calendar', 'v3', credentials=cred)
            return api_service.calendarList().get(calendarId=calendar_id).execute()
        except HttpError as err:
            if err.resp.status == 404:
                return None
            else:
                raise

    def get_busy_slots_for_calendar(self, email, calendar_id, start, end, tz):
        if DOMAIN.casefold() == "GOOGLE".casefold():
            return self.get_busy_slots_for_calendar_google(email, calendar_id, start, end, tz)
        elif DOMAIN.casefold() == "OFFICE".casefold():
            return self.get_busy_slots_for_calendar_office(email, calendar_id, start, end, tz)

    def _freebusy_office(self, email, calendar_id, start, end, tz):
        endpoint = (f"/users/{email}/calendars/{calendar_id}/events?"
                    f"$filter=((start/dateTime le '{start}'and end/dateTime ge '{end}') "
                    f"or (start/dateTime ge '{start}'and start/dateTime le '{end}') "
                    f"or (end/dateTime ge '{start}'and end/dateTime le '{end}')) "
                    f"and showAs ne 'free'")
        return requests.get(
            f'https://graph.microsoft.com/v1.0/{endpoint}',
            headers={'Authorization': f'Bearer {self.token["access_token"]}',
                     'Prefer': f'outlook.timezone = "{tz}"'}
        ).json().get('value', [])

    def get_busy_slots_for_calendar_office(
            self,
            email: str,
            calendar_id: str,
            start: Optional[datetime.datetime] = None,
            end: Optional[datetime.datetime] = None,
            tz: str = "Pacific Standard Time",
    ) -> list[BusySlot]:
        if not calendar_id:
            calendar_id = self._get_user_default_calendar_office(email).get('id')
        resp = self._freebusy_office(
            email=email,
            calendar_id=calendar_id,
            start=start.replace(tzinfo=None).isoformat(),
            end=end.replace(tzinfo=None).isoformat(),
            tz=tz
        )
        return [
            BusySlot(
                start=pytz.timezone(tz).localize(parse(slot['start']['dateTime'])),
                end=pytz.timezone(tz).localize(parse(slot['end']['dateTime']))
            )
            for slot in resp
        ]

    def get_busy_slots_for_calendar_google(
            self,
            email: str,
            calendar_id: Optional[str] = None,
            start: Optional[datetime.datetime] = None,
            end: Optional[datetime.datetime] = None,
            tz: str = BS_AS_TIMEZONE,
    ) -> list[BusySlot]:
        """
        Returns:
            [
                {
                    'start': '2021-06-13T21:00:00-03:00',
                    'end': '2021-06-13T22:00:00-03:00'
                },
                {
                    'start': '2021-06-13T22:30:00-03:00',
                    'end': '2021-06-13T23:30:00-03:00'
                }
            ]
            or
            [] if there are no events from `start` to `end` on `calendar_id`

        """
        if not calendar_id:
            calendar_id = email
        body = {
            "timeMin": start.isoformat(),
            "timeMax": end.isoformat(),
            "timeZone": tz,
            "items": [{'id': calendar_id}]
        }
        cred = self.cred.with_subject(email)
        api_service = build('calendar', 'v3', credentials=cred)
        resp = api_service.freebusy().query(body=body).execute()

        calendars = resp['calendars']
        busy_slots = calendars.get(calendar_id, {'busy': []})
        slots = busy_slots['busy']
        return [
            BusySlot(start=parse(slot['start']), end=parse(slot['end']))
            for slot in slots
        ]

    def get_free_slots_for_calendar(self,
                                    email: str,
                                    cal_id: str,
                                    start_date: dt.datetime,
                                    end_date: dt.datetime) -> list[FreeSlot]:
        """Get free time slots of a calendar by iterating with a cursor over busy time slots."""
        free_slots = []
        cursor = start_date
        busy_slots_response = self.get_busy_slots_for_calendar(email,
                                                               cal_id,
                                                               start_date,
                                                               end_date,
                                                               tz=self.BS_AS_TIMEZONE)
        busy_slots = [slot.to_dict() for slot in busy_slots_response]

        for slot in busy_slots:
            start, end = parse(slot['start']), parse(slot['end'])
            if start < start_date or end > end_date:
                # Event does not belong to the current timeframe
                continue
            if cursor < start:
                # There is a free slot until next event starts
                free_slots.append(FreeSlot(cursor, start))
                cursor = end
            elif cursor >= start:
                if cursor < end:
                    # This time slot is occupied, advance the cursor
                    cursor = end
                elif cursor >= end:
                    # Event has already happened
                    continue

        if cursor < end_date:
            # There's time left until the end of the day
            free_slots.append(FreeSlot(cursor, end_date))

        return free_slots

    def _is_free_slot_available_by_duration(self, duration, slot):
        slot_start, slot_end = parse(slot['start']), parse(slot['end'])
        SATURDAY, SUNDAY = 5, 6
        NON_WORKING_DAYS = (SATURDAY, SUNDAY)
        if slot_start.weekday() in NON_WORKING_DAYS or slot_end.weekday() in NON_WORKING_DAYS:
            return None
        minutes_diff = (slot_end - slot_start).total_seconds() / 60.0
        if minutes_diff >= duration:
            return FreeSlot(slot_start, slot_end)
        else:
            return None

    def _find_meeting_slot_with_multiple_cals(
            self, busy_slots_list, duration, start, end, time_start, time_end
    ) -> list[MeetingSlot]:
        """
        Start y end determinan el rango de fechas en el cual se quiere realizar la reunion.
        Se recibe tambien una lista de los espacios ocupados por todos los calendarios
         que van a asistir a la misma.
        Llenas el rango de las fechas que diste en start y end con estos espacios ocupados cada 5 minutos
         y luego, mediante una diferencia, obtenes los espacios que tenes disponibles cada 5 minutos
         dentro de ese rango dado previamente.
        Para terminar, recorres cada espacio que tenes cada 5 minutos hasta encontrar alguno que,
         si le sumas la duracion de la reunion, tambien este ese espacio disponible, siempre y cuando
         tenga los espacios en el medio tambien disponibles. Es por esto que se compara una suma de la
         duracion contra una posicion especificia dentro de la lista de los espacios disponibles. Esa
         posicion especifica es un multiplo de 5 (porque usamos espacios cada 5 minutos) y es por esto
         que se especifica previamente que la duracion tiene que ser multiplo de 5.
        Como ultimo paso le realiza un checkeo por si fallo el algoritmo por algun motivo cosmico y este
         espacio se agrega a la lista de espacios disponibles que tenes cada 5 minutos con el rango
         de la duracion de la reunion. Despues sera necesario elegir uno de ellos a eleccion del usuario.
        """
        meeting_slot_list = []
        position = int(duration / 5)
        dif = pd.date_range(start=start.isoformat(), end=end.isoformat(), freq='5T')
        if busy_slots_list:
            combined = pd.date_range(
                busy_slots_list[0]['start'],
                busy_slots_list[0]['end'],
                freq='5T'
            )
            for busy_slot in busy_slots_list[1:]:
                combined = combined.union(pd.date_range(busy_slot['start'], busy_slot['end'], freq='5T'))
            dif = dif.difference(combined)

        pos = dif.indexer_between_time(time_start, time_end)
        newdif = [dif[p] for p in pos]

        for slot in newdif:
            if newdif.index(slot) + duration / 5 < len(newdif):
                if (newdif[newdif.index(slot)] + pd.Timedelta(minutes=duration)) \
                        == newdif[newdif.index(slot) + position]:
                    slot_start = newdif[newdif.index(slot)]
                    slot_end = newdif[newdif.index(slot) + position]
                    slot_to_use = FreeSlot(slot_start, slot_end).to_dict()
                    viable_slot = self._is_free_slot_available_by_duration(
                        slot=slot_to_use,
                        duration=duration
                    )
                    if viable_slot:
                        meeting_slot_list.append(MeetingSlot(
                            start=viable_slot.start,
                            end=viable_slot.start + datetime.timedelta(minutes=duration)
                        ))
                        return meeting_slot_list  # Por ahora vamos a cortar en el primero que encuentre
        return meeting_slot_list

    def organize_meeting(
            self,
            meeting_room: str,
            cals: list[str],
            duration: int,
            start: datetime.date,
            end: datetime.date,
            time_start: datetime.time,
            time_end: datetime.time,
            tz: str = BS_AS_TIMEZONE
    ) -> list[MeetingSlot]:
        """Given calendars, return all the available time slots

        Details:
            - Some calendars have specified working hours (9AM-4PM), we should honor that restrictions
            - Time slot should be greater or equal to meeting duration
            - Eventually, we should be able to parametrize de amount of attendees, prepare for that.
            - It would also be nice to have an argument (here or in another function)
              to give more than 1 meeting option
        """
        timezone = pytz.timezone(tz)
        start = timezone.localize(datetime.datetime.combine(start, time_start))
        end = timezone.localize(datetime.datetime.combine(end, time_end))
        busy_slots_list = []
        if meeting_room != 'virtual':
            meeting_room_slots_response = self.get_busy_slots_for_calendar(
                email=DOMAIN_ADMIN_ACC,
                calendar_id=meeting_room,
                start=start - datetime.timedelta(minutes=5),
                end=end + datetime.timedelta(minutes=5),
                tz=tz
            )
            busy_slots_list = [slot.to_dict() for slot in meeting_room_slots_response]
        for cal_id in cals:
            slots_response = self.get_busy_slots_for_calendar(
                email=cal_id,
                calendar_id=None,
                start=start - datetime.timedelta(minutes=5),
                end=end + datetime.timedelta(minutes=5),
                tz=tz
            )
            for slot in slots_response:
                busy_slots_list.append(slot.to_dict())

        return self._find_meeting_slot_with_multiple_cals(
            busy_slots_list, duration, start, end, time_start, time_end
        )
