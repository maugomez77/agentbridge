from pathlib import Path
from agentbridge.config import ensure_dirs
from agentbridge.db import store
from agentbridge.models.artifact import Artifact, ArtifactType
from agentbridge.ingestors import get_ingestor


async def seed_demo():
    ensure_dirs()
    existing = store.get_project("Demo Store API")
    if existing:
        return

    project = store.create_project(
        name="Demo Store API",
        base_url="https://fakestoreapi.com",
    )
    sample = Path(__file__).parent.parent.parent.parent / "templates" / "sample-openapi.yaml"
    if not sample.exists():
        return

    content = sample.read_text()
    artifact = Artifact(
        project_id=project.id,
        name=sample.name,
        type=ArtifactType.openapi,
        source_path=str(sample),
        raw_content=content,
    )
    store.create_artifact(artifact)

    ingestor_cls = get_ingestor("openapi")
    ingestor = ingestor_cls()

    result, endpoints = await ingestor.ingest(artifact)
    store.update_artifact(result)
    store.save_endpoints(endpoints)
    project.artifact_count = len(store.list_artifacts(project.id))
    project.tool_count = len(store.get_endpoints_by_project(project.id))
    store.update_project(project)
