import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class Box(BaseModel):
    __tablename__ = 'box'
    __table_args__ = (UniqueConstraint('name', 'working_space_id', name="unique_by_working_space_and_name"), )
    id = Column(Integer, primary_key=True)
    working_space_id = Column(Integer, ForeignKey("working_space.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    reservation = relationship("Reservation", backref='box')

    def to_dict(self):
        return {
            'id': self.id,
            'working_space_id': self.working_space_id,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())
