from pathlib import Path
import json
from agentbridge.models.project import Project
from agentbridge.models.artifact import Artifact
from agentbridge.models.endpoint import Endpoint
from agentbridge.config import settings


class Store:
    def __init__(self):
        self._projects_file = settings.data_dir / "projects.json"
        self._artifacts_file = settings.data_dir / "artifacts.json"
        self._endpoints_file = settings.data_dir / "endpoints.json"
        self._projects: list[Project] = []
        self._artifacts: list[Artifact] = []
        self._endpoints: list[Endpoint] = []
        self._load()

    def _load(self):
        if self._projects_file.exists():
            data = json.loads(self._projects_file.read_text())
            self._projects = [Project(**p) for p in data]
        if self._artifacts_file.exists():
            data = json.loads(self._artifacts_file.read_text())
            self._artifacts = [Artifact(**a) for a in data]
        if self._endpoints_file.exists():
            data = json.loads(self._endpoints_file.read_text())
            self._endpoints = [Endpoint(**e) for e in data]

    def _save_projects(self):
        self._projects_file.write_text(json.dumps([p.model_dump(mode="json") for p in self._projects], indent=2, default=str))

    def _save_artifacts(self):
        self._artifacts_file.write_text(json.dumps([a.model_dump(mode="json") for a in self._artifacts], indent=2, default=str))

    def _save_endpoints(self):
        self._endpoints_file.write_text(json.dumps([e.model_dump(mode="json") for e in self._endpoints], indent=2, default=str))

    def create_project(self, name: str, base_url: str | None = None) -> Project:
        project = Project(name=name, base_url=base_url)
        self._projects.append(project)
        self._save_projects()
        return project

    def get_project(self, name: str) -> Project | None:
        for p in self._projects:
            if p.name == name:
                return p
        return None

    def get_project_by_id(self, project_id: str) -> Project | None:
        for p in self._projects:
            if p.id == project_id:
                return p
        return None

    def list_projects(self) -> list[Project]:
        return list(self._projects)

    def update_project(self, project: Project):
        for i, p in enumerate(self._projects):
            if p.id == project.id:
                project.updated_at = __import__("datetime").datetime.now()
                self._projects[i] = project
                self._save_projects()
                return

    def create_artifact(self, artifact: Artifact) -> Artifact:
        self._artifacts.append(artifact)
        self._save_artifacts()
        return artifact

    def get_artifact(self, artifact_id: str) -> Artifact | None:
        for a in self._artifacts:
            if a.id == artifact_id:
                return a
        return None

    def list_artifacts(self, project_id: str | None = None) -> list[Artifact]:
        if project_id:
            return [a for a in self._artifacts if a.project_id == project_id]
        return list(self._artifacts)

    def update_artifact(self, artifact: Artifact):
        for i, a in enumerate(self._artifacts):
            if a.id == artifact.id:
                artifact.updated_at = __import__("datetime").datetime.now()
                self._artifacts[i] = artifact
                self._save_artifacts()
                return

    def save_endpoints(self, endpoints: list[Endpoint]):
        for ep in endpoints:
            existing = [e for e in self._endpoints if e.id == ep.id]
            if not existing:
                self._endpoints.append(ep)
        self._save_endpoints()

    def get_endpoints(self, artifact_id: str | None = None) -> list[Endpoint]:
        if artifact_id:
            return [e for e in self._endpoints if e.artifact_id == artifact_id]
        return list(self._endpoints)

    def get_endpoints_by_project(self, project_id: str) -> list[Endpoint]:
        artifact_ids = {a.id for a in self._artifacts if a.project_id == project_id}
        return [e for e in self._endpoints if e.artifact_id in artifact_ids]


store = Store()
