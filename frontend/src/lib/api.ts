const API_BASE = window.location.origin.includes('vercel.app')
  ? 'https://agentbridge-demo.onrender.com/api'
  : '/api'

function _getToken(): string | null {
  return localStorage.getItem('agentbridge-token')
}

export function getApiKey(): string | null {
  return localStorage.getItem('agentbridge-apikey')
}

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  const token = _getToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  return headers
}

async function fetcher<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { ...authHeaders(), ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    const err = await res.text()
    throw new Error(err)
  }
  return res.json()
}

export function getToken(): string | null {
  return localStorage.getItem('agentbridge-token')
}

export function setToken(token: string) {
  localStorage.setItem('agentbridge-token', token)
}

export function removeToken() {
  localStorage.removeItem('agentbridge-token')
}

export function setApiKey(key: string) {
  localStorage.setItem('agentbridge-apikey', key)
}

export function removeApiKey() {
  localStorage.removeItem('agentbridge-apikey')
}

export async function login(email: string, password: string) {
  const data = await fetcher<{ access_token: string; user: Record<string, unknown> }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
  setToken(data.access_token)
  return data.user
}

export async function register(email: string, password: string, display_name?: string) {
  const data = await fetcher<{ access_token: string; user: Record<string, unknown> }>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, display_name }),
  })
  setToken(data.access_token)
  return data.user
}

export async function fetchMe() {
  return fetcher<{ id: string; email: string; display_name: string | null; tier: string; api_key: string | null; created_at: string }>('/auth/me')
}

export async function generateApiKey() {
  return fetcher<{ api_key: string }>('/auth/api-keys', { method: 'POST' })
}

export async function revokeApiKey() {
  return fetcher<{ message: string }>('/auth/api-keys', { method: 'DELETE' })
}

export async function regenerateApiKey() {
  return fetcher<{ api_key: string }>('/auth/api-keys/regenerate', { method: 'POST' })
}

export async function fetchSubscription() {
  return fetcher<{ id: string; tier: string; current_period_start: string | null; current_period_end: string | null; cancel_at_period_end: boolean }>('/billing/subscription')
}

export async function fetchTiers() {
  return fetcher<Array<{ tier: string; price_monthly: number; price_yearly: number; endpoints: number; teams: number; features: string[]; highlighted: boolean }>>('/billing/tiers')
}

export async function upgradeTier(tier: string) {
  return fetcher<{ message: string; tier: string }>('/billing/upgrade', {
    method: 'POST',
    body: JSON.stringify({ tier }),
  })
}

export async function cancelSubscription() {
  return fetcher<{ message: string }>('/billing/cancel', { method: 'POST' })
}

export async function reactivateSubscription() {
  return fetcher<{ message: string }>('/billing/reactivate', { method: 'POST' })
}

export async function downgradeTier() {
  return fetcher<{ message: string; tier: string }>('/billing/downgrade', { method: 'POST' })
}

export async function fetchTeams() {
  return fetcher<Array<{ id: string; name: string; owner_id: string; member_ids: string[]; created_at: string }>>('/teams')
}

export async function createTeam(name: string) {
  return fetcher<{ id: string; name: string; owner_id: string; member_ids: string[]; created_at: string }>('/teams', {
    method: 'POST',
    body: JSON.stringify({ name }),
  })
}

export async function addTeamMember(teamId: string, email: string) {
  return fetcher<{ message: string }>(`/teams/${teamId}/members`, {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
}

export async function removeTeamMember(teamId: string, memberId: string) {
  return fetcher<{ message: string }>(`/teams/${teamId}/members/${memberId}`, { method: 'DELETE' })
}

export async function deleteTeam(teamId: string) {
  return fetcher<{ message: string }>(`/teams/${teamId}`, { method: 'DELETE' })
}

export async function fetchUsage(days: number = 7) {
  return fetcher<Array<{ date: string; count: number }>>(`/usage?days=${days}`)
}

export async function fetchUsageCount() {
  return fetcher<{ total: number; limit: number; remaining: number }>('/usage/count')
}

export const RENDER_URL = 'https://agentbridge-demo.onrender.com'

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
  return fetcher<Array<{ name: string; description: string; input_schema: Record<string, unknown>; endpoint: Record<string, unknown> }>>(`/endpoints/by-project/${projectId}`)
}
