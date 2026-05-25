import json
from pathlib import Path
from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod


class PostmanIngestor(BaseIngestor):
    artifact_type = ArtifactType.postman

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if path_lower.endswith(".json"):
            if content:
                return '"info"' in content[:200] and '"item"' in content[:500]
            return False
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or Path(artifact.source_path).read_text()
            collection = json.loads(raw)
            endpoints = []
            def walk_items(items, parent_tags=None):
                for item in items:
                    tags = (parent_tags or []) + [item.get("name", "")]
                    if "request" in item:
                        req = item["request"]
                        method = req.get("method", "GET").upper()
                        url_data = req.get("url", {})
                        path = url_data.get("path", [])
                        if isinstance(path, list):
                            path_str = "/" + "/".join(str(p) for p in path)
                        else:
                            path_str = str(path)
                        try:
                            http_method = HttpMethod(method)
                        except ValueError:
                            continue
                        endpoints.append(Endpoint(
                            artifact_id=artifact.id,
                            method=http_method,
                            path=path_str,
                            summary=tags[-1] if tags else None,
                            tags=[t for t in tags if t],
                        ))
                    if "item" in item:
                        walk_items(item["item"], tags)
            walk_items(collection.get("item", []))
            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []
