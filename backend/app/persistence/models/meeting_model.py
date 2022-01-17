import datetime
import json

import pytz
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class Meeting(BaseModel):
    __tablename__ = 'meeting'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    meeting_room_id = Column(Integer, ForeignKey("meeting_room.id", ondelete="CASCADE"), nullable=True)
    meeting_request_id = Column(Integer, ForeignKey("meeting_request.id", ondelete="CASCADE"), nullable=False)
    date = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    description = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    event = Column(String, nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    meeting_user = relationship("MeetingUser", cascade="all,delete", backref='meeting')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meeting_room_id': self.meeting_room_id,
            'meeting_request_id': self.meeting_request_id,
            'date': self.date,
            'duration': self.duration,
            'description': self.description,
            'summary': self.summary,
            'event': self.event
        }

    def to_json(self):
        return json.dumps(self.to_dict())
