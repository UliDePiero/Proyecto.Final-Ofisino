import datetime
import json
import logging
import os

import msal
from google.oauth2 import service_account
from flask import abort
from loguru import logger

from app.calendar_class import DOMAIN


def get_service_credentials():
    """Get service account credentials from google api or raise ValueError"""
    scopes = ['https://www.googleapis.com/auth/calendar',
              'https://www.googleapis.com/auth/admin.directory.user']

    CREDENTIALS_FILE_NAME = 'service_credentials.json'
    if os.path.exists(CREDENTIALS_FILE_NAME):
        return service_account.Credentials.from_service_account_file(
            'service_credentials.json',
            scopes=scopes
        )
    else:
        raise ValueError(f'Invalid credentials, check if {CREDENTIALS_FILE_NAME} exists on {os.getcwd()}')


OFFICE_CONFIG = {
    "client_id": os.getenv('OFFICE_CLIENT_ID', 'MISSING_KEY'),
    "secret": os.getenv('OFFICE_SECRET', 'MISSING_KEY'),
    "authority": f"https://login.microsoftonline.com/{os.getenv('OFFICE_TENANT_ID', 'MISSING_KEY')}",
    "scope": ["https://graph.microsoft.com/.default"]  # Default means those registered within app.
}


def _get_token_from_office():
    logger.info('Trying to create a new instance of a client app')
    client = msal.ConfidentialClientApplication(
        OFFICE_CONFIG["client_id"],
        authority=OFFICE_CONFIG["authority"],
        client_credential=OFFICE_CONFIG["secret"],
        validate_authority=False
    )
    logger.info('Trying to get a new token with the client app')
    result = client.acquire_token_silent(OFFICE_CONFIG["scope"], account=None)
    if not result:
        logging.info("No suitable token exists in cache. Let's get a new one from AAD.")
        result = client.acquire_token_for_client(scopes=OFFICE_CONFIG["scope"])

    assert 'access_token' in result, f"Error authenticating against office API. Response:\n{result}"
    dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=result['expires_in'])
    result['expires_datetime'] = dt.isoformat()
    with open('token.json', 'w') as write_file:
        json.dump(result, write_file)
    return result


def get_office_credentials():
    try:
        if os.path.exists('token.json'):
            logger.info('Checking existing credentials')
            with open('token.json', "r") as read_file:
                token = json.load(read_file)
            if token.get('token_type') == 'Bearer':
                if (datetime.datetime.utcnow()
                        < datetime.datetime.fromisoformat(token.get('expires_datetime'))):
                    return token
                else:
                    logger.info('Token expired, trying to get a new one')
                    token = _get_token_from_office()
                    return token
            else:
                logger.info('Invalid token, trying to get a new one')
                token = _get_token_from_office()
                return token
        else:
            logger.info('Token not found, trying to get a valid token')
            token = _get_token_from_office()
            return token
    except Exception():
        raise ValueError(f'Invalid credentials, check if the Office credentials are set on .env file')


def get_service_credentials_or_abort_with_http_500():
    """Get Config for Calendar Manager or raise HTTP 500 if it fails.

    Useful if being called from a view handling an http request
    """
    if DOMAIN.casefold() == "GOOGLE".casefold():
        logger.info('Getting credentials from google')
        try:
            return get_service_credentials()
        except ValueError:
            abort(500, description="No se encuentran las credenciales de servicio de Google.")
    elif DOMAIN.casefold() == "OFFICE".casefold():
        logger.info('Getting credentials from office')
        try:
            return get_office_credentials()
        except ValueError:
            abort(500, description="No se encuentran las credenciales de Office.")
    else:
        abort(500, description="No esta establecido ningún tipo de dominio.{GOOGLE/OFFICE}")
