from pydantic import BaseModel, ConfigDict, EmailStr


class APILogCreate(BaseModel):
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None


class APILogList(BaseModel):
    id: int
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class APILogRetrieve(BaseModel):
    id: int
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ErrorLogCreate(BaseModel):
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None


class ErrorLogList(BaseModel):
    id: int
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ErrorLogRetrieve(BaseModel):
    id: int
    url: str
    method: str
    ip: str | None = None
    user_agent: str | None = None
    body: dict | None = {}
    header: dict | None = None
    response: dict | None = None
    system_details: dict | None = {}
    extra_field: dict | None = None
    user_id: int | None = None
    status_code: str | None = None

    model_config = ConfigDict(from_attributes=True)
