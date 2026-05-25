import asyncio
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.markdown import Markdown
from agentbridge.config import ensure_dirs
from agentbridge.db import store
from agentbridge.models.artifact import Artifact, ArtifactType
from agentbridge.ingestors import detect_type, get_ingestor

app = typer.Typer(
    name="agentbridge",
    help="Turn any API artifact into an MCP server",
    no_args_is_help=True,
)
console = Console()


@app.callback()
def callback():
    ensure_dirs()


@app.command()
def init(
    name: str = typer.Argument(..., help="Project name"),
    base_url: str = typer.Option(None, "--base-url", "-u", help="Base URL of the upstream API"),
):
    existing = store.get_project(name)
    if existing:
        console.print(f"[yellow]Project '{name}' already exists[/]")
        return
    project = store.create_project(name=name, base_url=base_url)
    console.print(Panel(f"[bold green]✓[/] Project [bold]{project.name}[/] initialized", box=box.ROUNDED))
    console.print(f"  ID:       {project.id}")
    console.print(f"  Base URL: {project.base_url or '(not set)'}")
    console.print(f"  Artifacts: 0  Tools: 0")
    console.print("\n[yellow]Next:[/] [bold]agentbridge add <file>[/] to ingest an artifact")


@app.command()
def add(
    path: str = typer.Argument(..., help="Path to artifact file (OpenAPI, Postman, SQL, etc.)"),
    project: str = typer.Option(None, "--project", "-p", help="Project name (defaults to active project)"),
):
    projects = store.list_projects()
    if not projects:
        console.print("[red]No projects found. Create one first:[/] agentbridge init <name>")
        raise typer.Exit(1)

    proj = store.get_project(project) if project else projects[0]
    if not proj:
        console.print(f"[red]Project '{project}' not found[/]")
        raise typer.Exit(1)

    from pathlib import Path
    p = Path(path)
    if not p.exists():
        console.print(f"[red]File not found: {path}[/]")
        raise typer.Exit(1)

    content = p.read_text(encoding="utf-8")
    detected = detect_type(path, content)
    if not detected:
        console.print("[red]Could not detect artifact type. Supported: OpenAPI, Postman, GraphQL, DB schemas[/]")
        raise typer.Exit(1)

    artifact = Artifact(
        project_id=proj.id,
        name=p.name,
        type=ArtifactType(detected),
        source_path=str(p),
        raw_content=content,
    )
    store.create_artifact(artifact)

    ingestor_cls = get_ingestor(detected)
    ingestor = ingestor_cls()

    async def run():
        result_artifact, endpoints = await ingestor.ingest(artifact)
        store.update_artifact(result_artifact)
        store.save_endpoints(endpoints)
        proj.artifact_count = len(store.list_artifacts(proj.id))
        proj.tool_count = len(store.get_endpoints_by_project(proj.id))
        store.update_project(proj)
        return result_artifact, endpoints

    result, endpoints = asyncio.run(run())
    if result.status.value == "error":
        console.print(f"[red]Ingestion failed:[/] {result.error_message}")
        raise typer.Exit(1)

    console.print(Panel(f"[bold green]✓[/] Ingested [bold]{result.name}[/] as [bold]{detected}[/]", box=box.ROUNDED))
    console.print(f"  Endpoints found: [bold]{result.endpoint_count}[/]")
    console.print(f"  Project: {proj.name}  Tools: {proj.tool_count}")
    console.print("\n[yellow]Next:[/] [bold]agentbridge serve[/] to start the MCP server")


@app.command()
def serve(
    port: int = typer.Option(8080, "--port", "-p", help="MCP server port"),
    project: str = typer.Option(None, "--project", "-p", help="Project to serve"),
):
    projects = store.list_projects()
    if not projects:
        console.print("[red]No projects found. Create one first:[/] agentbridge init <name>")
        raise typer.Exit(1)

    proj = store.get_project(project) if project else projects[0]
    if not proj:
        console.print(f"[red]Project '{project}' not found[/]")
        raise typer.Exit(1)

    endpoints = store.get_endpoints_by_project(proj.id)
    if not endpoints:
        console.print("[yellow]No artifacts ingested yet. Add one:[/] agentbridge add <file>")
        raise typer.Exit(1)

    table = Table(title=f"MCP Tools for [bold]{proj.name}[/]", box=box.ROUNDED)
    table.add_column("Tool", style="cyan")
    table.add_column("Method", style="green")
    table.add_column("Path", style="yellow")
    table.add_column("Auth")
    from agentbridge.generators.mcp_v1 import generate_tool_definitions
    tools = generate_tool_definitions(endpoints, proj)
    for t in tools:
        meta = t.get("_meta", {})
        table.add_row(
            t["name"],
            meta.get("method", "GET"),
            meta.get("path", "/"),
            "✓" if meta.get("auth_required") else "—",
        )
    console.print(table)

    import uvicorn
    from agentbridge.api.server import app as fastapi_app
    from agentbridge.api.mcp import router as mcp_router, set_active_project

    set_active_project(proj.id)
    fastapi_app.include_router(mcp_router)

    console.print(f"\n[green]MCP server running on http://localhost:{port}/mcp[/]")
    console.print(f"[dim]Configure your agent:[/]")
    console.print(f"[bold]  opencode.json:[/] {{\"mcpServers\": {{\"agentbridge\": {{\"url\": \"http://localhost:{port}/mcp\"}}}}}}")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port, log_level="info")


@app.command()
def dashboard(
    port: int = typer.Option(5173, "--port", "-p", help="Dashboard port"),
):
    console.print("[green]Opening dashboard...[/]")
    console.print(f"Dashboard URL: [bold]http://localhost:{port}[/]")
    import subprocess, sys
    subprocess.Popen(["npm", "run", "dev", "--", "--port", str(port)], cwd=str(Path(__file__).parent.parent.parent.parent / "frontend"))


@app.command(name="list")
def list_projects():
    projects = store.list_projects()
    if not projects:
        console.print("[yellow]No projects yet. Create one:[/] agentbridge init <name>")
        return
    table = Table(title="Projects", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Artifacts", justify="right")
    table.add_column("Tools", justify="right")
    table.add_column("Base URL")
    for p in projects:
        table.add_row(p.name, str(p.artifact_count), str(p.tool_count), p.base_url or "—")
    console.print(table)


@app.command()
def list_artifacts(
    project: str = typer.Option(None, "--project", "-p", help="Filter by project"),
):
    artifacts = store.list_artifacts()
    if project:
        proj = store.get_project(project)
        if proj:
            artifacts = store.list_artifacts(proj.id)
    if not artifacts:
        console.print("[yellow]No artifacts yet[/]")
        return
    table = Table(title="Artifacts", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Endpoints", justify="right")
    table.add_column("Project")
    for a in artifacts:
        proj = store.get_project_by_id(a.project_id)
        table.add_row(
            a.name,
            a.type.value,
            {"pending": "○", "ingesting": "⋯", "ready": "✓", "error": "✗"}.get(a.status.value, "?"),
            str(a.endpoint_count),
            proj.name if proj else "—",
        )
    console.print(table)


if __name__ == "__main__":
    app()
