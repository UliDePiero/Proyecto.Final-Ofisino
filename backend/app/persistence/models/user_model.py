import datetime
import json

import pytz
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    domain_id = Column(String, default=None, nullable=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    avatar_url = Column(String, default=None, nullable=True)
    admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    reservation = relationship("Reservation", backref='user')
    meeting_request = relationship("MeetingRequest", backref='user')
    meeting_request_user = relationship("MeetingRequestUser", backref='user')
    meeting_user = relationship("MeetingUser", backref='user')
    meeting = relationship("Meeting", backref='user')
    # TODO: Add reference to organization

    def to_dict(self):
        return {
            'id': self.id,
            'domain_id': self.domain_id,
            'name': self.name,
            'email': self.email,
            'avatar_url': self.avatar_url,
            'admin': self.admin
        }

    def to_json(self):
        return json.dumps(self.to_dict())
