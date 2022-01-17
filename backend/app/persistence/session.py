"""See https://docs.sqlalchemy.org/en/14/orm/contextual.html?
highlight=scoped_session#using-thread-local-scope-with-web-applications"""
import flask
from flask import g
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.api_config import get_config


def get_session():
    if 'session' not in g:
        g.session = _create_session(get_config().DATABASE_URL)
    return g.session


def _create_session(db_url):
    engine = get_engine(db_url)
    return scoped_session(sessionmaker(engine), scopefunc=flask._app_ctx_stack.__ident_func__)


def get_engine(db_url):
    return create_engine(db_url)


def close_session(exception=None):
    session = g.pop('session', None)
    if session is not None:
        session.remove()
