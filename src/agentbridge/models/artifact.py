from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class ArtifactType(str, Enum):
    openapi = "openapi"
    postman = "postman"
    graphql = "graphql"
    db_schema = "db_schema"
    docs = "docs"
    spring_mvc = "spring_mvc"
    wsdl = "wsdl"
    grpc = "grpc"


class ArtifactStatus(str, Enum):
    pending = "pending"
    ingesting = "ingesting"
    ready = "ready"
    error = "error"


class Artifact(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str
    name: str
    type: ArtifactType
    status: ArtifactStatus = ArtifactStatus.pending
    source_path: str | None = None
    raw_content: str | None = None
    parsed_model: dict | None = None
    endpoint_count: int = 0
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


import uuid
