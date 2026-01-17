from postgresql_audit import versioning_manager
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


versioning_manager.init(Base)
