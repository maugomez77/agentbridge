from abc import ABC, abstractmethod
from agentbridge.models.artifact import Artifact, ArtifactType
from agentbridge.models.endpoint import Endpoint


class BaseIngestor(ABC):
    artifact_type: ArtifactType

    @classmethod
    @abstractmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        ...

    @abstractmethod
    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        ...
