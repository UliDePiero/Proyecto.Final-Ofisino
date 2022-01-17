import datetime

import pytz
from flask import json
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class WorkingSpace(BaseModel):
    __tablename__ = 'working_space'
    __table_args__ = (UniqueConstraint('name', 'building_id', name="unique_by_building_and_name"),)
    id = Column(Integer, primary_key=True)
    building_id = Column(Integer, ForeignKey("building.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    area = Column(Integer, nullable=False)
    square_meters_per_box = Column(Integer)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    box = relationship("Box", backref='workingspace')

    def to_dict(self):
        return {
            'id': self.id,
            'building_id': self.building_id,
            'name': self.name,
            'area': self.area,
            'square_meters_per_box': self.square_meters_per_box,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())
