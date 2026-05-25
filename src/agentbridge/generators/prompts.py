from agentbridge.models.endpoint import Endpoint, HttpMethod
from agentbridge.models.project import Project


def generate_prompts(endpoints: list[Endpoint], project: Project) -> list[dict]:
    """Generate MCP prompts that teach agents how to use the tools effectively."""
    prompts: list[dict] = []

    entities = _infer_entities(endpoints)
    grouped = _group_by_entity(endpoints, entities)

    for entity, eps in grouped.items():
        prompts.append({
            "name": f"workflow_{entity}",
            "description": f"How to work with {entity} — list, get, create, update, delete operations",
            "arguments": [],
            "content": _build_workflow_prompt(entity, eps, project),
        })

    for ep in endpoints[:20]:
        prompts.append({
            "name": f"howto_{_safe_name(ep.summary or ep.path)}",
            "description": f"Usage guide for {ep.method.value} {ep.path}",
            "arguments": [],
            "content": _build_endpoint_prompt(ep, project),
        })

    return prompts


def generate_resources(endpoints: list[Endpoint], project: Project) -> list[dict]:
    """Generate MCP resources that describe the API surface."""
    resources: list[dict] = []

    for ep in endpoints:
        resources.append({
            "uri": f"tool://{project.id}/{_safe_name(ep.summary or ep.path.rsplit('/', 1)[-1])}",
            "name": ep.summary or ep.path,
            "description": f"{ep.method.value} {ep.path} — {ep.description or 'no description'}",
            "mimeType": "application/json",
        })

    return resources


def _safe_name(s: str) -> str:
    result = ''.join(c if c.isalnum() or c == '_' else '_' for c in s)
    return result.lower().strip('_')


def _infer_entities(endpoints: list[Endpoint]) -> list[str]:
    seen: set[str] = set()
    for ep in endpoints:
        parts = [p for p in ep.path.split('/') if p and not p.startswith('{')]
        if parts:
            seen.add(parts[-1])
    return sorted(seen)


def _group_by_entity(endpoints: list[Endpoint], entities: list[str]) -> dict[str, list[Endpoint]]:
    groups: dict[str, dict[str, Endpoint]] = {}
    for ep in endpoints:
        parts = [p for p in ep.path.split('/') if p and not p.startswith('{')]
        entity = parts[-1] if parts else 'default'
        for e in entities:
            if e in ep.path:
                entity = e
                break
        if entity not in groups:
            groups[entity] = {}
        groups[entity][ep.method.value] = ep
    return {e: list(eps.values()) for e, eps in groups.items()}


def _build_workflow_prompt(entity: str, endpoints: list[Endpoint], project: Project) -> str:
    lines = [f"# Working with {entity.replace('_', ' ').title()} on {project.name}", ""]
    lines.append(f"This API provides the following operations for {entity.replace('_', ' ')}:")
    lines.append("")

    verbs = {ep.method.value: ep.path for ep in endpoints}

    if 'GET' in verbs:
        lines.append(f"1. **List all**: Call `{_safe_name('list_' + entity)}` to retrieve {entity} with optional filters.")
    if 'GET' in verbs and any('{' in p for _, p in verbs.items()):
        lines.append(f"2. **Get by ID**: Call `{_safe_name('get_' + entity)}` with an `id` parameter to fetch a single {entity}.")
    if 'POST' in verbs:
        lines.append(f"3. **Create**: Call `{_safe_name('create_' + entity)}` with the required fields to create a new {entity}.")
    if 'PUT' in verbs or 'PATCH' in verbs:
        lines.append(f"4. **Update**: Use the update endpoint with the {entity} ID and the fields to modify.")
    if 'DELETE' in verbs:
        lines.append(f"5. **Delete**: Pass the {entity} ID to remove it.")

    lines.append("")
    lines.append("## Best practices")
    lines.append("- Always list first to see available data before creating or updating.")
    lines.append("- Validate required parameters before calling any endpoint.")
    lines.append("- Handle pagination when listing large datasets.")
    lines.append("")
    lines.append(f"Base URL: {project.base_url or '(not configured)'}")

    return '\n'.join(lines)


def _build_endpoint_prompt(ep: Endpoint, project: Project) -> str:
    lines = [f"# {ep.method.value} {ep.path}", ""]
    if ep.description:
        lines.append(ep.description)
        lines.append("")

    if ep.parameters:
        lines.append("## Parameters")
        lines.append("")
        for p in ep.parameters:
            req = "**required**" if p.required else "optional"
            lines.append(f"- `{p.name}` ({p.type}, {req}): {p.description or 'no description'}")
        lines.append("")

    lines.append("## Example usage")
    args = {}
    for p in ep.parameters:
        if p.required:
            args[p.name] = f'<{p.type}>'
    lines.append("```json")
    lines.append(str({"arguments": args} if args else {"arguments": {}}))
    lines.append("```")
    lines.append("")
    lines.append(f"Base URL: {project.base_url or '(not configured)'}")

    return '\n'.join(lines)
