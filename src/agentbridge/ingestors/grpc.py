import re
from pathlib import Path
from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter


class GrpcIngestor(BaseIngestor):
    artifact_type = ArtifactType.grpc

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        if path.lower().endswith('.proto'):
            return True
        if content and ('service ' in content or 'rpc ' in content) and 'syntax = ' in content:
            return True
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or Path(artifact.source_path).read_text()
            endpoints: list[Endpoint] = []

            # Find all service blocks
            for service_match in re.finditer(r'service\s+(\w+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', raw):
                service_name = service_match.group(1)
                service_body = service_match.group(2)

                # Find all rpc definitions within the service
                for rpc_match in re.finditer(r'rpc\s+(\w+)\s*\(\s*(?:stream\s+)?(\w+)\s*\)\s*returns\s*\(\s*(?:stream\s+)?(\w+)\s*\)', service_body):
                    rpc_name = rpc_match.group(1)
                    input_type = rpc_match.group(2)
                    output_type = rpc_match.group(3)

                    # Look for a description comment above the rpc
                    desc = _find_proto_comment(service_body, rpc_name)

                    endpoints.append(Endpoint(
                        artifact_id=artifact.id,
                        method=HttpMethod.post,
                        path=f'/{service_name}/{rpc_name}',
                        summary=rpc_name,
                        description=desc or f'gRPC {rpc_name} — request: {input_type}, response: {output_type}',
                        parameters=[
                            Parameter(name='body', location='body', type=input_type, required=True, description=f'Message type: {input_type}')
                        ],
                        tags=[service_name, 'grpc'],
                    ))

            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []


def _find_proto_comment(text: str, rpc_name: str) -> str | None:
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if f'rpc {rpc_name}' in line:
            comments = []
            j = i - 1
            while j >= 0 and lines[j].strip().startswith('//'):
                comments.insert(0, lines[j].strip().lstrip('/').strip())
                j -= 1
            if comments:
                return ' '.join(comments)
    return None
