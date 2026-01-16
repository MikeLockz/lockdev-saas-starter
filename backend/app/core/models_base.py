from sqlalchemy.orm import DeclarativeBase
from postgresql_audit import versioning_manager

class Base(DeclarativeBase):
    pass

versioning_manager.init(Base)