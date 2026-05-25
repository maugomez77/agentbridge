import { useEffect, useState } from 'react'
import { fetchHealth, fetchStatus, fetchProjects } from '../lib/api'
import { Link } from 'react-router-dom'
import {
  FolderKanban,
  FileCode2,
  Puzzle,
  Activity,
  ArrowRight,
  Sparkles,
  Plus,
  ExternalLink,
} from 'lucide-react'

export default function Dashboard() {
  const [health, setHealth] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [projects, setProjects] = useState<any[]>([])

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth(null))
    fetchStatus().then(setStats).catch(() => setStats(null))
    fetchProjects().then(setProjects).catch(() => setProjects([]))
  }, [])

  const cards = [
    { label: 'Projects', value: stats?.projects ?? '—', icon: FolderKanban, gradient: 'from-violet-500 to-indigo-600', accent: 'bg-violet-500/10 text-violet-600' },
    { label: 'Artifacts', value: stats?.artifacts ?? '—', icon: FileCode2, gradient: 'from-emerald-500 to-teal-600', accent: 'bg-emerald-500/10 text-emerald-600' },
    { label: 'MCP Tools', value: stats?.tools ?? '—', icon: Puzzle, gradient: 'from-amber-500 to-orange-600', accent: 'bg-amber-500/10 text-amber-600' },
  ]

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
        <div>
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Dashboard</h1>
          <p className="text-sm text-slate-500 mt-1.5">Bridge your APIs to AI agents in seconds</p>
        </div>
        <Link
          to="/projects"
          className="inline-flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/25 hover:shadow-indigo-600/40"
        >
          <Sparkles size={16} />
          New Project
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
        {cards.map(card => {
          const Icon = card.icon
          return (
            <div key={card.label} className="group relative overflow-hidden rounded-2xl bg-white border border-slate-200/60 p-6 hover:shadow-lg hover:border-slate-300 transition-all duration-300">
              <div className="flex items-start justify-between mb-4">
                <div className={`p-2.5 rounded-xl ${card.accent.split(' ')[0]}`}>
                  <Icon size={22} className={card.accent.split(' ')[1]} />
                </div>
                <div className={`h-1 w-12 rounded-full bg-gradient-to-r ${card.gradient} opacity-0 group-hover:opacity-100 transition-opacity duration-500`} />
              </div>
              <p className="text-4xl font-bold text-slate-900 tracking-tight">{card.value}</p>
              <p className="text-sm text-slate-500 mt-1">{card.label}</p>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3 bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-slate-800">Recent Projects</h2>
            <Link to="/projects" className="text-xs text-indigo-600 hover:text-indigo-700 font-semibold inline-flex items-center gap-1 transition-colors">
              View all <ArrowRight size={12} />
            </Link>
          </div>
          {projects.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
                <FolderKanban size={28} className="text-slate-400" />
              </div>
              <h3 className="text-base font-semibold text-slate-700 mb-1">No projects yet</h3>
              <p className="text-sm text-slate-400 mb-6 max-w-xs mx-auto">Create your first project to start turning API specs into MCP tools</p>
              <Link
                to="/projects"
                className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
              >
                <Plus size={15} />
                Create Project
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {projects.map(p => (
                <Link
                  key={p.id}
                  to={`/projects/${p.id}`}
                  className="flex items-center justify-between p-4 rounded-xl hover:bg-slate-50 transition-all border border-transparent hover:border-slate-200 group/row"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-xl bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold text-sm">
                      {p.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <div className="flex items-center gap-1.5">
                        <p className="text-sm font-semibold text-slate-800 group-hover/row:text-indigo-700 transition-colors">{p.name}</p>
                        <ExternalLink size={12} className="text-slate-300 group-hover/row:text-indigo-400 transition-colors" />
                      </div>
                      <div className="flex items-center gap-3 mt-0.5">
                        <span className="text-xs text-slate-400">{p.artifact_count} artifact{p.artifact_count !== 1 ? 's' : ''}</span>
                        <span className="w-1 h-1 rounded-full bg-slate-300" />
                        <span className="text-xs text-slate-400">{p.tool_count} tool{p.tool_count !== 1 ? 's' : ''}</span>
                      </div>
                    </div>
                  </div>
                  <ArrowRight size={16} className="text-slate-300 group-hover/row:text-indigo-500 transition-colors" />
                </Link>
              ))}
            </div>
          )}
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6">
            <h2 className="text-lg font-semibold text-slate-800 mb-5">API Status</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-xl bg-slate-50 border border-slate-100">
                <div className="flex items-center gap-3">
                  <Activity size={18} className={health ? 'text-emerald-500' : 'text-slate-300'} />
                  <span className="text-sm font-medium text-slate-700">Backend</span>
                </div>
                <div className="flex items-center gap-2">
                  {health ? (
                    <>
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                      <span className="text-xs text-emerald-600 font-medium uppercase tracking-wide">{health.status}</span>
                    </>
                  ) : (
                    <span className="text-xs text-slate-400">Connecting...</span>
                  )}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-slate-800">
                <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">MCP Endpoint</p>
                <p className="text-sm font-mono text-emerald-300 break-all leading-relaxed">
                  https://agentbridge-demo.onrender.com/mcp/
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-2xl border border-indigo-100 p-6">
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                <Sparkles size={16} className="text-white" />
              </div>
              <div>
                <p className="text-sm font-semibold text-indigo-800 mb-1">Ready for any AI agent</p>
                <p className="text-xs text-indigo-600 leading-relaxed">
                  Connect Claude, Cursor, Copilot, or any MCP-compatible agent to consume your APIs natively. No extra setup required.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
