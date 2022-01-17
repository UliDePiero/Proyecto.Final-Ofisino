import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class MeetingRequest(BaseModel):
    __tablename__ = 'meeting_request'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    conditions = Column(JSON, nullable=False)
    summary = Column(String, default=None)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    meeting_request_user = relationship("MeetingRequestUser", cascade="all,delete", backref='meeting_request')
    meeting = relationship("Meeting", backref='meeting_request')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'conditions': self.conditions,
            'summary': self.summary,
            'status': self.status,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
