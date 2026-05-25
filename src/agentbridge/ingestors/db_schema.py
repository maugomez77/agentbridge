from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod


class DBSchemaIngestor(BaseIngestor):
    artifact_type = ArtifactType.db_schema

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if path_lower.endswith((".sql", ".prisma", ".drizzle")):
            return True
        if content and ("CREATE TABLE" in content or "model " in content and "{" in content):
            return True
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or ""
            endpoints = []
            tables = []
            if "CREATE TABLE" in raw:
                for line in raw.split("\n"):
                    if "CREATE TABLE" in line:
                        parts = line.replace("CREATE TABLE", "").strip().split("(")
                        if parts:
                            tables.append(parts[0].strip().strip('"`'))
            if "model " in raw:
                for line in raw.split("\n"):
                    stripped = line.strip()
                    if stripped.startswith("model ") and "{" in stripped:
                        name = stripped.replace("model ", "").split("{")[0].strip()
                        tables.append(name)
            has_db_url = artifact.source_path and artifact.source_path.endswith(".sql") if False else False
            endpoints.append(Endpoint(
                artifact_id=artifact.id,
                method=HttpMethod.get,
                path="/db/schema",
                summary="Database Schema",
                description=f"SQL database schema with {len(tables)} tables",
                tags=["database", "schema"],
            ))
            artifact.parsed_model = {"tables": tables}
            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []
