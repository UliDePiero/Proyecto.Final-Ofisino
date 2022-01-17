"""
To execute this script first go to Google Cloud Console and get the service_credentials.json
Then run python calendar_class.py
"""
import datetime

import pytz

from app.api_credentials import get_service_credentials
from app.calendar_class import CalendarManager


def main():
    service_credentials = get_service_credentials()
    cman = CalendarManager(config=service_credentials)

    bsas = pytz.timezone('America/Argentina/Buenos_Aires')
    start = bsas.fromutc(datetime.datetime.utcnow()).replace(microsecond=0)
    end = start.replace(hour=23, minute=59)

    list_user_cals = cman.get_all_users_calendars()

    for dic in list_user_cals:
        print(dic['user'])
        for cal in dic['cals']:
            print('ID:', cal['id'])
            busy = cman.get_busy_slots_for_calendar(
                dic['email'],
                cal['id'],
                start,
                end,
                tz=cman.BS_AS_TIMEZONE)
            print(busy)


if __name__ == '__main__':
    main()
