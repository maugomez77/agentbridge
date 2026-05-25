from agentbridge.models.endpoint import Endpoint
from agentbridge.models.project import Project


def generate_tool_definitions(endpoints: list[Endpoint], project: Project) -> list[dict]:
    tools = []
    for ep in endpoints:
        tool_name = ep.summary or _default_tool_name(ep)
        tool_name = _sanitize_name(tool_name)
        properties = {}
        required = []
        for p in ep.parameters:
            properties[p.name] = {
                "type": p.type,
                "description": p.description or "",
            }
            if p.required:
                required.append(p.name)
        tools.append({
            "name": tool_name,
            "description": ep.description or ep.summary or f"{ep.method.value} {ep.path}",
            "input_schema": {
                "type": "object",
                "properties": properties,
                "required": required if required else None,
            },
            "_meta": {
                "method": ep.method.value,
                "path": ep.path,
                "auth_required": ep.auth_required,
                "tags": ep.tags,
            },
        })
    return tools


def generate_mcp_server_code(tools: list[dict], project: Project) -> str:
    lines = []
    lines.append("from mcp.server import FastMCP")
    lines.append("from pydantic import BaseModel")
    lines.append("")
    lines.append(f'server = FastMCP("{project.name}")')
    lines.append("")
    for tool in tools:
        name = tool["name"]
        params = tool["input_schema"]
        props = params.get("properties", {})
        func_params = ", ".join(props.keys()) if props else ""
        lines.append("")
        lines.append("@server.tool()")
        lines.append(f"async def {name}({func_params}):")
        lines.append(f'    """{tool["description"]}"""')
        lines.append('    pass  # generated from artifact')
        lines.append("")
    lines.append("")
    lines.append('if __name__ == "__main__":')
    lines.append("    server.run()")
    return "\n".join(lines)


def _sanitize_name(name: str) -> str:
    result = ""
    for c in name:
        if c.isalnum() or c == "_":
            result += c
        elif c in (" ", "-"):
            result += "_"
    while result.startswith("_"):
        result = result[1:]
    while result.endswith("_"):
        result = result[:-1]
    return result.lower().replace("__", "_") or "unnamed_tool"


def _default_tool_name(ep: Endpoint) -> str:
    path_parts = [p for p in ep.path.split("/") if p and not p.startswith("{")]
    name = "_".join(path_parts) if path_parts else "root"
    return f"{ep.method.value.lower()}_{name}"
