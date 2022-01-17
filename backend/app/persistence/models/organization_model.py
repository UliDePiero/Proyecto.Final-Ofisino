import datetime
import json

import pytz
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

from app.persistence.basemodel import BaseModel
from app.persistence.timezone_var import TZ


class Organization(BaseModel):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=pytz.timezone(TZ).fromutc(datetime.datetime.utcnow()))
    deleted_at = Column(DateTime, default=None)
    building = relationship("Building", backref='organization')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }

    def to_json(self):
        return json.dumps(self.to_dict())
