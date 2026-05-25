import re
from pathlib import Path
from agentbridge.ingestors.base import BaseIngestor
from agentbridge.models.artifact import Artifact, ArtifactType, ArtifactStatus
from agentbridge.models.endpoint import Endpoint, HttpMethod, Parameter


_ANNOTATION_TO_METHOD = {
    'GetMapping': 'GET', 'PostMapping': 'POST', 'PutMapping': 'PUT',
    'DeleteMapping': 'DELETE', 'PatchMapping': 'PATCH', 'RequestMapping': None,
}


class SpringMVCIngestor(BaseIngestor):
    artifact_type = ArtifactType.spring_mvc

    @classmethod
    def can_handle(cls, path: str, content: str | None = None) -> bool:
        path_lower = path.lower()
        if not path_lower.endswith('.java'):
            return False
        if content:
            return any(a in content for a in ['@RestController', '@Controller', '@RequestMapping', '@GetMapping', '@PostMapping'])
        return 'Controller' in Path(path).stem or 'Resource' in Path(path).stem

    async def ingest(self, artifact: Artifact) -> tuple[Artifact, list[Endpoint]]:
        try:
            raw = artifact.raw_content or Path(artifact.source_path).read_text()
            endpoints: list[Endpoint] = []

            # Find base class-level path
            base_path = ''
            base_match = re.search(r'@RequestMapping\s*\((?:\s*value\s*=\s*)?["\']([^"\']+)["\']', raw)
            if base_match:
                base_path = base_match.group(1)

            # Find all method-level endpoint annotations
            for name, method in _ANNOTATION_TO_METHOD.items():
                pattern = rf'@(?:\w+\.)?{name}\s*\((.*?)\)\s*\n\s*(?:public|private|protected)\s+\w+\s+(\w+)\s*\('
                for m in re.finditer(pattern, raw, re.DOTALL):
                    ann_content = m.group(1)
                    method_name = m.group(2)

                    # Extract path from annotation
                    path_match = re.search(r'(?:value|path)\s*=\s*["\']([^"\']+)["\']', ann_content)
                    path = path_match.group(1) if path_match else ''
                    full_path = '/' + base_path.strip('/') + '/' + path.strip('/')
                    full_path = re.sub(r'/+', '/', full_path)

                    http_method = method or _detect_method(method_name)

                    if http_method is None:
                        # @RequestMapping with method=RequestMethod.GET/POST/etc
                        method_match = re.search(r'method\s*=\s*(?:RequestMethod\.)?(\w+)', ann_content)
                        http_method = method_match.group(1).upper() if method_match else 'GET'

                    params = _extract_params(raw, method_name)

                    endpoints.append(Endpoint(
                        artifact_id=artifact.id,
                        method=HttpMethod(http_method),
                        path=full_path,
                        summary=method_name,
                        description=_extract_javadoc(raw, method_name),
                        parameters=params,
                        tags=[Path(artifact.source_path).stem] if artifact.source_path else [],
                    ))

            artifact.endpoint_count = len(endpoints)
            artifact.status = ArtifactStatus.ready
            return artifact, endpoints
        except Exception as e:
            artifact.status = ArtifactStatus.error
            artifact.error_message = str(e)
            return artifact, []


def _detect_method(name: str) -> str | None:
    for prefix in ['get', 'find', 'list', 'fetch', 'search', 'read']:
        if name.lower().startswith(prefix): return 'GET'
    for prefix in ['create', 'add', 'save', 'insert', 'post']:
        if name.lower().startswith(prefix): return 'POST'
    for prefix in ['update', 'edit', 'modify', 'put', 'patch']:
        if name.lower().startswith(prefix): return 'PUT'
    for prefix in ['delete', 'remove', 'destroy']:
        if name.lower().startswith(prefix): return 'DELETE'
    return 'GET'


def _extract_params(source: str, method_name: str) -> list[Parameter]:
    params: list[Parameter] = []
    # Find the method body to scope param extraction
    method_start = source.find(f' {method_name}(')
    if method_start == -1:
        return params
    method_end = source.find('{', method_start)
    method_sig = source[method_start:method_end + 1] if method_end > method_start else source[method_start:]

    for ptype, loc, pattern in [
        ('path', 'path', r'@PathVariable\s*(?:\([^)]*\))?\s*(?:\w+\s+)+(\w+)'),
        ('query', 'query', r'@RequestParam\s*(?:\([^)]*\))?\s*(?:\w+\s+)+(\w+)'),
        ('body', 'body', r'@RequestBody\s*(?:\w+\s+)+(\w+)'),
    ]:
        for pm in re.finditer(pattern, method_sig):
            param_name = pm.group(1)
            # Extract param type (the word before the name)
            type_match = re.search(rf'(\w+)\s+{re.escape(param_name)}\b', method_sig)
            param_type = type_match.group(1) if type_match else 'string'
            params.append(Parameter(
                name=param_name,
                location=loc,
                type=_map_java_type(param_type),
                required=loc == 'path',
            ))
    return params


def _extract_javadoc(source: str, method_name: str) -> str | None:
    pattern = rf'/\*\*\s*\n\s*\*\s*(.*?)\s*\n\s*\*/\s*\n\s*(?:@\w+\(.*?\)\s*\n\s*)*\s*(?:public|private|protected).*\b{re.escape(method_name)}\s*\('
    match = re.search(pattern, source, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def _map_java_type(java_type: str) -> str:
    mapping = {
        'String': 'string', 'int': 'integer', 'Integer': 'integer',
        'long': 'integer', 'Long': 'integer', 'double': 'number',
        'Double': 'number', 'boolean': 'boolean', 'Boolean': 'boolean',
        'List': 'array', 'Map': 'object', 'void': 'null',
    }
    return mapping.get(java_type, 'string')
