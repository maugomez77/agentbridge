from agentbridge.config import ensure_dirs
from agentbridge.db import store
from agentbridge.models.artifact import Artifact, ArtifactType
from agentbridge.ingestors import get_ingestor


_DEMO_SPEC = """openapi: 3.0.3
info:
  title: Fake Store API
  version: 1.0.0
  description: Free fake REST API for testing — products, carts, users
servers:
  - url: https://fakestoreapi.com
paths:
  /products:
    get:
      summary: List all products
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
      responses:
        '200':
          description: List of products
  /products/{id}:
    get:
      summary: Get a single product
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Product details
  /carts:
    get:
      summary: List all carts
      responses:
        '200':
          description: List of carts
  /carts/{id}:
    get:
      summary: Get a single cart
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: Cart details
  /users:
    get:
      summary: List all users
      responses:
        '200':
          description: List of users
"""


async def seed_demo():
    ensure_dirs()
    existing = store.get_project("Demo Store API")
    if existing and store.list_artifacts(existing.id):
        return

    project = existing or store.create_project(
        name="Demo Store API",
        base_url="https://fakestoreapi.com",
    )

    artifact = Artifact(
        project_id=project.id,
        name="sample-openapi.yaml",
        type=ArtifactType.openapi,
        raw_content=_DEMO_SPEC,
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
