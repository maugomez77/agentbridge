import yaml
from pathlib import Path
from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter


class OpenAPIIngestor(BaseIngestor):
    artifact_type = ArtifactType.openapi

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if path_lower.endswith((".yaml", ".yml", ".json")):
            if content:
                return "openapi" in content[:500] or "swagger" in content[:500].lower()
            return True
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or Path(artifact.source_path).read_text()
            is_yaml = (
                (artifact.source_path and artifact.source_path.endswith((".yaml", ".yml")))
                or raw.strip().startswith(("openapi:", "swagger:", "---"))
                or "openapi:" in raw[:100]
            )
            spec = yaml.safe_load(raw) if is_yaml else __import__("json").loads(raw)
            endpoints = []
            base_path = spec.get("basePath", "")
            for path, methods in spec.get("paths", {}).items():
                for method, details in methods.items():
                    try:
                        http_method = HttpMethod(method.upper())
                    except ValueError:
                        continue
                    params = []
                    for p in details.get("parameters", []):
                        params.append(Parameter(
                            name=p["name"],
                            location=p.get("in", "query"),
                            type=p.get("schema", {}).get("type", "string"),
                            required=p.get("required", False),
                            description=p.get("description"),
                        ))
                    endpoints.append(Endpoint(
                        artifact_id=artifact.id,
                        method=http_method,
                        path=base_path + path,
                        summary=details.get("summary"),
                        description=details.get("description"),
                        parameters=params,
                        tags=details.get("tags", []),
                    ))
            artifact.parsed_model = {"version": spec.get("openapi") or spec.get("swagger")}
            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []
