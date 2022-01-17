import datetime
import json

import pytz
from sqlalchemy import Column, Integer, ForeignKey, DateTime

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class MeetingRequestUser(BaseModel):
    __tablename__ = 'meeting_request_user'

    id = Column(Integer, primary_key=True)
    meeting_request_id = Column(Integer, ForeignKey("meeting_request.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)

    def to_dict(self):
        return {
            'id': self.id,
            'meeting_request_id': self.meeting_request_id,
            'user_id': self.user_id,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
