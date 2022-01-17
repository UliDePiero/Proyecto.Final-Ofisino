import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, JSON, UniqueConstraint, ForeignKey, DateTime

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class MeetingRoom(BaseModel):
    __tablename__ = 'meeting_room'
    __table_args__ = (UniqueConstraint('name', 'building_id', name="unique_by_building2_and_name"),)
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    features = Column(JSON, nullable=False)
    calendar = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    building_id = Column(Integer, ForeignKey("building.id"), nullable=False)

    # Esto sera un dict de las caracteristicas que tendra la sala de reunion
    # El formato del JSON será con los defaults:
    # {
    #     aire_acondicionado: 0,
    #     computadoras: 0,
    #     proyector: 0,
    #     ventanas: 0,
    #     sillas: 0,
    #     mesas: 0
    # }

    def to_dict(self):
        return {
            'id': self.id,
            'building_id': self.building_id,
            'name': self.name,
            'capacity': self.capacity,
            'features': self.features,
            'calendar': self.calendar,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())
