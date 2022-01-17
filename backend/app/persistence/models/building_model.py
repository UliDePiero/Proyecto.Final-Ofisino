import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class Building(BaseModel):
    __tablename__ = 'building'
    __table_args__ = (UniqueConstraint('name', 'organization_id', name="unique_by_organization_and_name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    location = Column(String)
    description = Column(String, nullable=True)
    organization_id = Column(Integer, ForeignKey("organization.id"), nullable=False)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    meeting_room = relationship("MeetingRoom", backref='building')
    working_space = relationship("WorkingSpace", backref='building')

    def to_dict(self):
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'location': self.location,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())
