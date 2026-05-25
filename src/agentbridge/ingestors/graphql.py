from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter


class GraphQLIngestor(BaseIngestor):
    artifact_type = ArtifactType.graphql

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if path_lower.endswith((".graphql", ".gql", ".graphqls")):
            return True
        if content and ("type Query" in content or "type Mutation" in content or "schema {" in content):
            return True
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or ""
            endpoints = []
            base_url = "(graphql endpoint)"
            if raw:
                lines = raw.split("\n")
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("type Query"):
                        endpoints.append(Endpoint(
                            artifact_id=artifact.id,
                            method=HttpMethod.post,
                            path=base_url,
                            summary="GraphQL Queries",
                            description="All query operations defined in the schema",
                            tags=["graphql", "query"],
                        ))
                    if stripped.startswith("type Mutation"):
                        endpoints.append(Endpoint(
                            artifact_id=artifact.id,
                            method=HttpMethod.post,
                            path=base_url,
                            summary="GraphQL Mutations",
                            description="All mutation operations defined in the schema",
                            tags=["graphql", "mutation"],
                        ))
            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []
