import { useEffect, useState } from 'react'
import { fetchArtifacts, fetchProjects } from '../lib/api'
import {
  FileJson,
  Braces,
  FileCode2,
  Database,
  FileText,
  Layers,
  Filter,
  CheckCircle2,
  XCircle,
  Clock,
} from 'lucide-react'

const typeMeta: Record<string, { icon: typeof FileCode2; label: string; classes: string }> = {
  openapi: { icon: FileJson, label: 'OpenAPI', classes: 'bg-blue-50 text-blue-600 border-blue-200' },
  postman: { icon: Braces, label: 'Postman', classes: 'bg-orange-50 text-orange-600 border-orange-200' },
  graphql: { icon: FileCode2, label: 'GraphQL', classes: 'bg-pink-50 text-pink-600 border-pink-200' },
  db_schema: { icon: Database, label: 'DB Schema', classes: 'bg-purple-50 text-purple-600 border-purple-200' },
  docs: { icon: FileText, label: 'Docs', classes: 'bg-slate-50 text-slate-600 border-slate-200' },
}

const statusMeta: Record<string, { icon: typeof CheckCircle2; label: string; classes: string }> = {
  ready: { icon: CheckCircle2, label: 'Ready', classes: 'bg-emerald-50 text-emerald-600' },
  error: { icon: XCircle, label: 'Error', classes: 'bg-red-50 text-red-600' },
  pending: { icon: Clock, label: 'Pending', classes: 'bg-amber-50 text-amber-600' },
}

export default function Artifacts() {
  const [artifacts, setArtifacts] = useState<any[]>([])
  const [projects, setProjects] = useState<any[]>([])
  const [filter, setFilter] = useState('')

  useEffect(() => {
    fetchProjects().then(setProjects).catch(() => setProjects([]))
    fetchArtifacts().then(setArtifacts).catch(() => setArtifacts([]))
  }, [])

  const filtered = filter ? artifacts.filter(a => a.project_id === filter) : artifacts
  const projectName = (id: string) => projects.find(p => p.id === id)?.name || id

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
        <div>
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Artifacts</h1>
          <p className="text-sm text-slate-500 mt-1.5">All ingested API specifications and schemas</p>
        </div>
        <div className="flex items-center gap-2 bg-white border border-slate-200 rounded-xl px-4 py-2.5 shadow-sm">
          <Filter size={14} className="text-slate-400 flex-shrink-0" />
          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            className="text-sm bg-transparent border-none focus:outline-none text-slate-600 pr-2"
          >
            <option value="">All projects</option>
            {projects.map(p => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-5">
            <Layers size={32} className="text-indigo-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">No artifacts found</h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto mb-8">Upload an OpenAPI spec, Postman collection, or database schema to start generating MCP tools</p>
          <div className="inline-flex items-center gap-2 bg-slate-100 px-5 py-3 rounded-xl">
            <code className="text-sm text-slate-600 font-mono font-medium">agentbridge add ./openapi.yaml</code>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-6 py-4">Name</th>
                  <th className="text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-6 py-4">Type</th>
                  <th className="text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-6 py-4">Status</th>
                  <th className="text-right text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-6 py-4">Endpoints</th>
                  <th className="text-left text-[11px] font-semibold text-slate-400 uppercase tracking-wider px-6 py-4">Project</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50">
                {filtered.map(a => {
                  const meta = typeMeta[a.type] || typeMeta.docs
                  const TypeIcon = meta.icon
                  const st = statusMeta[a.status] || statusMeta.pending
                  const StatusIcon = st.icon
                  return (
                    <tr key={a.id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <TypeIcon size={17} className="text-slate-400 flex-shrink-0" />
                          <span className="text-sm font-medium text-slate-800">{a.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center text-[11px] font-semibold px-2.5 py-1 rounded-md border ${meta.classes}`}>
                          {meta.label}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-md ${st.classes}`}>
                          <StatusIcon size={12} />
                          {st.label}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <span className="inline-flex items-center justify-center w-8 h-6 rounded-lg bg-slate-100 text-xs font-bold text-slate-600">{a.endpoint_count}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-slate-500">{projectName(a.project_id)}</span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
