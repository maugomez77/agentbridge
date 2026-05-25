import { useEffect, useState } from 'react'
import { fetchProjects, createProject } from '../lib/api'
import { Link } from 'react-router-dom'
import {
  FolderKanban,
  Plus,
  X,
  ArrowRight,
  Globe,
} from 'lucide-react'

export default function Projects() {
  const [projects, setProjects] = useState<any[]>([])
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [baseUrl, setBaseUrl] = useState('')

  const load = () => fetchProjects().then(setProjects).catch(() => setProjects([]))
  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) return
    await createProject(name.trim(), baseUrl.trim() || undefined)
    setName('')
    setBaseUrl('')
    setShowForm(false)
    load()
  }

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
        <div>
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Projects</h1>
          <p className="text-sm text-slate-500 mt-1.5">Manage your API bridges for AI agents</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            showForm
              ? 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-600/25'
          }`}
        >
          {showForm ? <X size={16} /> : <Plus size={16} />}
          {showForm ? 'Cancel' : 'New Project'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 mb-8">
          <h3 className="text-base font-semibold text-slate-800 mb-5">Create a new project</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Project Name</label>
              <input
                value={name}
                onChange={e => setName(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all bg-slate-50 focus:bg-white"
                placeholder="e.g. stripe-api, shopify-store"
                required
              />
            </div>
            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                Base URL <span className="text-slate-300 font-normal normal-case">— optional</span>
              </label>
              <input
                value={baseUrl}
                onChange={e => setBaseUrl(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all bg-slate-50 focus:bg-white font-mono"
                placeholder="https://api.example.com/v1"
              />
            </div>
          </div>
          <button
            type="submit"
            className="mt-5 inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-sm"
          >
            <Plus size={16} />
            Create Project
          </button>
        </form>
      )}

      {projects.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-5">
            <FolderKanban size={32} className="text-indigo-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">No projects yet</h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto mb-8">Bridge your first API to AI agents by creating a project and adding an API specification</p>
          <button
            onClick={() => setShowForm(true)}
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/25"
          >
            <Plus size={18} />
            Create Your First Project
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {projects.map(p => (
            <Link
              key={p.id}
              to={`/projects/${p.id}`}
              className="block bg-white rounded-2xl border border-slate-200/60 shadow-sm p-5 hover:shadow-md hover:border-indigo-200 transition-all group"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4 min-w-0">
                  <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg shadow-md shadow-indigo-500/20 flex-shrink-0">
                    {p.name.charAt(0).toUpperCase()}
                  </div>
                  <div className="min-w-0">
                    <p className="font-semibold text-slate-800 group-hover:text-indigo-700 transition-colors truncate">{p.name}</p>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      {p.base_url ? (
                        <span className="flex items-center gap-1 text-xs text-slate-400 truncate">
                          <Globe size={11} className="flex-shrink-0" />
                          <span className="truncate">{p.base_url}</span>
                        </span>
                      ) : (
                        <span className="text-xs text-slate-300 italic">No base URL configured</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-6 flex-shrink-0">
                  <div className="hidden sm:flex items-center gap-5">
                    <div className="text-right">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Artifacts</p>
                      <p className="text-lg font-bold text-slate-700">{p.artifact_count}</p>
                    </div>
                    <div className="w-px h-10 bg-slate-200" />
                    <div className="text-right">
                      <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Tools</p>
                      <p className="text-lg font-bold text-slate-700">{p.tool_count}</p>
                    </div>
                  </div>
                  <ArrowRight size={18} className="text-slate-300 group-hover:text-indigo-500 group-hover:translate-x-0.5 transition-all" />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
