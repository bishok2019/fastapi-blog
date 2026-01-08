import enum

from sqlalchemy import JSON, Column, Enum, Integer, String

from base.models import BaseModel


class HTTPMethod(str, enum.Enum):
    get = "get"
    post = "post"
    put = "put"
    patch = "patch"
    delete = "delete"


class APILog(BaseModel):
    __tablename__ = "api_logs"

    url = Column(String(255), nullable=False)
    method = Column(String(50), nullable=False)
    ip = Column(String(255), nullable=True)
    user_agent = Column(String(255), nullable=True)

    body = Column(JSON, nullable=True, default=dict)
    header = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    system_details = Column(JSON, nullable=True, default=dict)
    extra_field = Column(JSON, nullable=True)

    user_id = Column(Integer, nullable=True)
    status_code = Column(String(50), nullable=True)


class ErrorLog(BaseModel):
    __tablename__ = "error_logs"

    url = Column(String(255), nullable=False)

    method = Column(
        Enum(HTTPMethod, name="http_method_enum"),
        nullable=False,
        default=HTTPMethod.get,
    )
    ip = Column(String(255), nullable=True)
    user_agent = Column(String(255), nullable=True)

    body = Column(JSON, nullable=True, default=dict)
    header = Column(JSON, nullable=True)
    response = Column(JSON, nullable=True)
    system_details = Column(JSON, nullable=True, default=dict)
    extra_field = Column(JSON, nullable=True)

    user_id = Column(Integer, nullable=True)
    status_code = Column(String(50), nullable=True)
