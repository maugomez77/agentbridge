EN = {
    "project_created": "Project '{name}' initialized",
    "artifact_ingested": "Ingested '{name}' as {type}",
    "no_projects": "No projects found. Create one: agentbridge init <name>",
    "no_artifacts": "No artifacts yet",
    "endpoints_found": "Endpoints found: {count}",
    "tools_generated": "Tools: {count}",
    "mcp_server_running": "MCP server running on http://localhost:{port}/mcp",
    "next_add_artifact": "Next: add an artifact with agentbridge add <file>",
    "next_serve": "Next: agentbridge serve to start the MCP server",
}

ES = {
    "project_created": "Proyecto '{name}' inicializado",
    "artifact_ingested": "Ingerido '{name}' como {type}",
    "no_projects": "No se encontraron proyectos. Crea uno: agentbridge init <nombre>",
    "no_artifacts": "Aún no hay artefactos",
    "endpoints_found": "Endpoints encontrados: {count}",
    "tools_generated": "Herramientas: {count}",
    "mcp_server_running": "Servidor MCP ejecutándose en http://localhost:{port}/mcp",
    "next_add_artifact": "Siguiente: agrega un artefacto con agentbridge add <archivo>",
    "next_serve": "Siguiente: agentbridge serve para iniciar el servidor MCP",
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    strings = ES if lang == "es" else EN
    template = strings.get(key, key)
    return template.format(**kwargs)
