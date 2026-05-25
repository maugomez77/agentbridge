from enum import Enum
from pydantic import BaseModel, Field


class HttpMethod(str, Enum):
    get = "GET"
    post = "POST"
    put = "PUT"
    patch = "PATCH"
    delete = "DELETE"
    head = "HEAD"
    options = "OPTIONS"


class Parameter(BaseModel):
    name: str
    location: str = "query"
    type: str = "string"
    required: bool = False
    description: str | None = None
    schema_ref: str | None = None


class Endpoint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    artifact_id: str
    method: HttpMethod
    path: str
    summary: str | None = None
    description: str | None = None
    parameters: list[Parameter] = Field(default_factory=list)
    request_body: dict | None = None
    response_schema: dict | None = None
    tags: list[str] = Field(default_factory=list)
    auth_required: bool = False
    auth_type: str | None = None


import uuid
