from agentbridge.ingestors.openapi import OpenAPIIngestor
from agentbridge.ingestors.postman import PostmanIngestor
from agentbridge.ingestors.graphql import GraphQLIngestor
from agentbridge.ingestors.db_schema import DBSchemaIngestor
from agentbridge.ingestors.spring_mvc import SpringMVCIngestor
from agentbridge.ingestors.wsdl import WSDLIngestor
from agentbridge.ingestors.grpc import GrpcIngestor

INGESTORS: dict[str, type] = {
    "openapi": OpenAPIIngestor,
    "postman": PostmanIngestor,
    "graphql": GraphQLIngestor,
    "db_schema": DBSchemaIngestor,
    "spring_mvc": SpringMVCIngestor,
    "wsdl": WSDLIngestor,
    "grpc": GrpcIngestor,
}


def detect_type(path: str, content: str | None = None) -> str | None:
    for name, cls in INGESTORS.items():
        if cls.can_handle(path, content):
            return name
    return None


def get_ingestor(name: str):
    cls = INGESTORS.get(name)
    if cls is None:
        raise ValueError(f"Unknown ingestor: {name}")
    return cls
