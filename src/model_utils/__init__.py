import uuid

def generateId():
    return str(uuid.uuid4())

from sqlalchemy import Column, String, DateTime, func, desc
from sqlalchemy.ext.declarative import declarative_base
from flask_jsontools import JsonSerializableBase


class MyBaseClass:

    id = Column(String, primary_key=True, default=generateId)
    creado = Column(DateTime, server_default=func.now())
    actualizado = Column(DateTime, onupdate=func.now())

    def __init__(self):
        self.id = generateId()

    @classmethod
    def findAll(cls, s):
        return s.query(cls).all()

Base = declarative_base(cls=(JsonSerializableBase,MyBaseClass))

class MyJsonBaseClass:

    def __json__(self, exluded_keys=set()):
        return self.__dict__
