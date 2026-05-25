import re
import xml.etree.ElementTree as ET
from pathlib import Path
from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter


class WSDLIngestor(BaseIngestor):
    artifact_type = ArtifactType.wsdl

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if path_lower.endswith('.wsdl') or path_lower.endswith('.xml'):
            if content:
                return '<wsdl:definitions' in content or '<definitions' in content or '<wsdl:portType' in content or '<portType' in content
            return 'wsdl' in path_lower
        return False

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or Path(artifact.source_path).read_text()
            root = ET.fromstring(raw)
            ns = _extract_namespaces(raw)
            endpoints: list[Endpoint] = []

            # Find portType operations
            for port_type in root.iter():
                tag = port_type.tag.split('}')[-1] if '}' in port_type.tag else port_type.tag
                if tag in ('portType', 'interface'):
                    for op in port_type:
                        op_tag = op.tag.split('}')[-1] if '}' in op.tag else op.tag
                        if op_tag == 'operation':
                            op_name = op.get('name', '')
                            input_msg = None
                            output_msg = None
                            doc_elem = None
                            for child in op:
                                child_tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                                if child_tag == 'input':
                                    input_msg = child.get('message', '')
                                elif child_tag == 'output':
                                    output_msg = child.get('message', '')
                                elif child_tag in ('documentation', 'wsdl:documentation'):
                                    doc_elem = child

                            # Try to resolve message parts
                            params: list[Parameter] = []
                            if input_msg:
                                msg_name = input_msg.split(':')[-1] if ':' in input_msg else input_msg
                                for msg in root.iter():
                                    msg_tag = msg.tag.split('}')[-1] if '}' in msg.tag else msg.tag
                                    if msg_tag == 'message' and msg.get('name') == msg_name:
                                        for part in msg:
                                            part_tag = part.tag.split('}')[-1] if '}' in part.tag else part.tag
                                            if part_tag == 'part':
                                                params.append(Parameter(
                                                    name=part.get('name', 'param'),
                                                    location='body',
                                                    type='string',
                                                    required=True,
                                                ))

                            endpoints.append(Endpoint(
                                artifact_id=artifact.id,
                                method=HttpMethod.post,
                                path=f'/wsdl/{op_name}',
                                summary=op_name,
                                description=doc_elem.text.strip() if doc_elem is not None and doc_elem.text else None,
                                parameters=params,
                                tags=['soap', 'wsdl'],
                            ))

            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []


def _extract_namespaces(raw: str) -> dict[str, str]:
    ns_map: dict[str, str] = {}
    for m in re.finditer(r'xmlns(?::(\w+))?=["\']([^"\']+)["\']', raw):
        prefix = m.group(1) or ''
        ns_map[prefix] = m.group(2)
    return ns_map
