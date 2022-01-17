import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class Reservation(BaseModel):
    __tablename__ = 'reservation'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    date = Column(Date, nullable=False)
    box_id = Column(Integer, ForeignKey("box.id"), nullable=False)
    event_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat(),
            'box_id': self.box_id,
            'event_id': self.event_id
        }

    def to_json(self):
        return json.dumps(self.to_dict())
