const RENDER_URL = 'https://agentbridge-demo.onrender.com'
const API_BASE = window.location.origin.includes('vercel.app') ? `${RENDER_URL}/api` : '/api'

async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err)
  }
  return res.json()
}

export function fetchHealth() {
  return fetch(`${RENDER_URL}/health`).then(r => r.json()) as Promise<{ status: string; version: string }>
}

export function fetchStatus() {
  return fetcher<{ projects: number; artifacts: number; tools: number }>('/status')
}

export function fetchProjects() {
  return fetcher<Array<{ id: string; name: string; base_url: string | null; artifact_count: number; tool_count: number; created_at: string }>>('/projects')
}

export function createProject(name: string, baseUrl?: string) {
  return fetcher<{ id: string; name: string }>('/projects', {
    method: 'POST',
    body: JSON.stringify({ name, base_url: baseUrl }),
  })
}

export function fetchArtifacts(projectId?: string) {
  const params = projectId ? `?project_id=${projectId}` : ''
  return fetcher<Array<{ id: string; name: string; type: string; status: string; endpoint_count: number; project_id: string }>>(`/artifacts${params}`)
}

export function fetchArtifact(artifactId: string) {
  return fetcher<{ id: string; name: string; type: string; status: string; endpoint_count: number; project_id: string; raw_content: string | null }>(`/artifacts/${artifactId}`)
}

export function uploadArtifact(projectId: string, name: string, content: string, type?: string) {
  return fetcher<{ id: string; name: string; type: string; status: string; endpoint_count: number }>('/artifacts', {
    method: 'POST',
    body: JSON.stringify({ project_id: projectId, name, raw_content: content, type: type || null }),
  })
}

export function fetchEndpointsByProject(projectId: string) {
  return fetcher<Array<{ name: string; description: string; input_schema: any; endpoint: any }>>(`/endpoints/by-project/${projectId}`)
}
