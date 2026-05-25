import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchProjects, fetchArtifacts, fetchEndpointsByProject, fetchArtifact, uploadArtifact } from '../lib/api'
import {
  ArrowLeft,
  Globe,
  FileCode2,
  Puzzle,
  Copy,
  CheckCheck,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  X,
  Eye,
  Upload,
  FileUp,
  Plus,
} from 'lucide-react'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<any>(null)
  const [artifacts, setArtifacts] = useState<any[]>([])
  const [tools, setTools] = useState<any[]>([])
  const [copied, setCopied] = useState(false)
  const [expandedTool, setExpandedTool] = useState<string | null>(null)
  const [viewedArtifact, setViewedArtifact] = useState<any>(null)
  const [artifactContent, setArtifactContent] = useState<string | null>(null)
  const [showImport, setShowImport] = useState(false)
  const [importContent, setImportContent] = useState('')
  const [importFile, setImportFile] = useState<File | null>(null)
  const [importing, setImporting] = useState(false)

  useEffect(() => {
    if (!id) return
    fetchProjects().then(ps => setProject(ps.find((p: any) => p.id === id)))
    fetchArtifacts(id).then(setArtifacts).catch(() => setArtifacts([]))
    fetchEndpointsByProject(id).then(setTools).catch(() => setTools([]))
  }, [id])

  const copyConfig = async () => {
    await navigator.clipboard.writeText(JSON.stringify({
      mcpServers: { agentbridge: { url: 'https://agentbridge-demo.onrender.com/mcp/' } }
    }, null, 2))
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const reloadArtifacts = () => {
    if (!id) return
    fetchProjects().then(ps => setProject(ps.find((p: any) => p.id === id)))
    fetchArtifacts(id).then(setArtifacts).catch(() => setArtifacts([]))
    fetchEndpointsByProject(id).then(setTools).catch(() => setTools([]))
  }

  const handleImport = async () => {
    if (!id || (!importContent && !importFile)) return
    setImporting(true)
    try {
      let content = importContent
      let filename = 'imported-spec.yaml'
      if (importFile) {
        content = await importFile.text()
        filename = importFile.name
      }
      await uploadArtifact(id, filename, content)
      setImportContent('')
      setImportFile(null)
      setShowImport(false)
      reloadArtifacts()
    } catch (e: any) {
      alert('Import failed: ' + (e.message || e))
    } finally {
      setImporting(false)
    }
  }

  const viewArtifact = async (artifact: any) => {
    setViewedArtifact(artifact)
    if (artifact.raw_content) {
      setArtifactContent(artifact.raw_content)
    } else {
      try {
        const full = await fetchArtifact(artifact.id)
        setArtifactContent(full.raw_content || '')
      } catch {
        setArtifactContent('Could not load artifact content.')
      }
    }
  }

  if (!project) return (
    <div className="p-10 max-w-6xl mx-auto flex justify-center py-24">
      <div className="animate-pulse flex flex-col items-center gap-4">
        <div className="w-12 h-12 rounded-2xl bg-slate-200" />
        <div className="w-40 h-4 rounded-full bg-slate-200" />
      </div>
    </div>
  )

  return (
    <div className="p-6 lg:p-10 max-w-6xl mx-auto">
      <Link to="/projects" className="inline-flex items-center gap-1.5 text-sm text-slate-400 hover:text-slate-600 mb-4 transition-colors font-medium">
        <ArrowLeft size={15} />
        Back to projects
      </Link>

      {/* Import section */}
      <div className="mb-6">
        {!showImport ? (
          <button
            onClick={() => setShowImport(true)}
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2.5 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-sm"
          >
            <Upload size={16} />
            Import Spec
          </button>
        ) : (
          <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <div className="p-1.5 rounded-lg bg-indigo-100">
                  <Upload size={16} className="text-indigo-600" />
                </div>
                <h3 className="font-semibold text-slate-800 text-sm">Import Artifact</h3>
              </div>
              <button onClick={() => setShowImport(false)} className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400">
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Upload file
                </label>
                <label className="flex flex-col items-center justify-center h-32 border-2 border-dashed border-slate-200 rounded-xl hover:border-indigo-300 hover:bg-indigo-50/30 transition-colors cursor-pointer">
                  <input
                    type="file"
                    className="hidden"
                    accept=".yaml,.yml,.json,.java,.proto,.wsdl,.sql,.prisma,.graphql,.gql"
                    onChange={e => {
                      const f = e.target.files?.[0]
                      if (f) {
                        setImportFile(f)
                        f.text().then(setImportContent)
                      }
                    }}
                  />
                  {importFile ? (
                    <div className="text-center">
                      <FileCode2 size={20} className="mx-auto text-indigo-500 mb-1" />
                      <p className="text-sm font-medium text-indigo-600">{importFile.name}</p>
                      <p className="text-xs text-slate-400 mt-0.5">{(importFile.size / 1024).toFixed(1)} KB</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <FileUp size={22} className="mx-auto text-slate-300 mb-2" />
                      <p className="text-xs font-medium text-slate-500">Drop file or click to browse</p>
                      <p className="text-[10px] text-slate-400 mt-1">.yaml .json .java .proto .wsdl .sql .prisma</p>
                    </div>
                  )}
                </label>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                  Or paste content
                </label>
                <textarea
                  value={importContent}
                  onChange={e => setImportContent(e.target.value)}
                  placeholder="Paste your OpenAPI YAML, Spring controller code, GraphQL schema, or any supported format..."
                  className="w-full h-32 border border-slate-200 rounded-xl px-4 py-3 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all resize-none bg-slate-50 focus:bg-white"
                />
              </div>
            </div>

            <div className="flex items-center justify-between mt-4">
              <p className="text-xs text-slate-400">
                Auto-detects: OpenAPI · Spring MVC · GraphQL · gRPC · WSDL · DB Schema · Postman
              </p>
              <button
                onClick={handleImport}
                disabled={!importContent.trim() || importing}
                className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                  importContent.trim() && !importing
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-sm'
                    : 'bg-slate-100 text-slate-400 cursor-not-allowed'
                }`}
              >
                {importing ? (
                  <>Importing...</>
                ) : (
                  <>
                    <Plus size={16} />
                    Import & Parse
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 lg:p-8 mb-8">
        <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-6 mb-8">
          <div className="flex items-start gap-5">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-indigo-600 flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-500/25 flex-shrink-0">
              {project.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">{project.name}</h1>
              {project.base_url ? (
                <div className="flex items-center gap-1.5 mt-2">
                  <Globe size={14} className="text-slate-400" />
                  <p className="text-sm text-slate-500 font-mono">{project.base_url}</p>
                  <ExternalLink size={12} className="text-slate-300" />
                </div>
              ) : (
                <p className="text-sm text-slate-400 mt-2 italic">No base URL configured</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-6 bg-slate-50 rounded-xl px-6 py-4">
            <div className="text-center">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Artifacts</p>
              <p className="text-2xl font-bold text-slate-700">{artifacts.length}</p>
            </div>
            <div className="w-px h-10 bg-slate-200" />
            <div className="text-center">
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">Tools</p>
              <p className="text-2xl font-bold text-indigo-600">{tools.length}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-50 rounded-xl p-5">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="p-1.5 rounded-lg bg-indigo-100">
                <FileCode2 size={16} className="text-indigo-600" />
              </div>
              <h2 className="font-semibold text-slate-800">Artifacts ({artifacts.length})</h2>
            </div>
            {artifacts.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No artifacts ingested yet</p>
            ) : (
              <div className="space-y-2.5">
                {artifacts.map(a => (
                  <button
                    key={a.id}
                    onClick={() => viewArtifact(a)}
                    className="w-full text-left flex items-center justify-between p-3 rounded-lg bg-white border border-slate-100 hover:border-indigo-200 hover:bg-indigo-50/50 transition-all group/artifact"
                  >
                    <div className="flex items-center gap-3">
                      <span className={`w-2 h-2 rounded-full ${a.status === 'ready' ? 'bg-emerald-500' : a.status === 'error' ? 'bg-red-500' : 'bg-amber-400'}`} />
                      <span className="text-sm font-medium text-slate-700 group-hover/artifact:text-indigo-700 transition-colors">{a.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-xs bg-slate-100 px-2.5 py-1 rounded-md text-slate-500 font-medium group-hover/artifact:bg-indigo-100 group-hover/artifact:text-indigo-600 transition-colors">{a.type}</span>
                      <span className="text-xs text-slate-400">{a.endpoint_count} endpoints</span>
                      <Eye size={14} className="text-slate-300 group-hover/artifact:text-indigo-400 transition-colors" />
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="bg-slate-50 rounded-xl p-5">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="p-1.5 rounded-lg bg-indigo-100">
                <Puzzle size={16} className="text-indigo-600" />
              </div>
              <h2 className="font-semibold text-slate-800">MCP Tools ({tools.length})</h2>
            </div>
            {tools.length === 0 ? (
              <p className="text-sm text-slate-400 py-6 text-center">No tools generated yet</p>
            ) : (
              <div className="space-y-2">
                {tools.map((t, i) => {
                  const isExpanded = expandedTool === t.name
                  const hasParams = t.input_schema?.properties && Object.keys(t.input_schema.properties).length > 0
                  return (
                    <div key={i} className="rounded-lg border border-slate-100 bg-white overflow-hidden transition-all">
                      <button
                        onClick={() => setExpandedTool(isExpanded ? null : t.name)}
                        className="w-full flex items-center justify-between p-3.5 hover:bg-slate-50 transition-colors text-left"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
                          <span className="text-sm font-mono font-medium text-slate-800 truncate">{t.name}</span>
                          {!hasParams && (
                            <span className="text-[10px] bg-slate-100 px-2 py-0.5 rounded-md text-slate-400 font-medium uppercase tracking-wider whitespace-nowrap ml-1">no args</span>
                          )}
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
                          <span className="text-xs text-slate-400 hidden sm:block">{t.description?.slice(0, 35)}{(t.description?.length ?? 0) > 35 ? '...' : ''}</span>
                          {isExpanded ? <ChevronDown size={15} className="text-slate-400" /> : <ChevronRight size={15} className="text-slate-400" />}
                        </div>
                      </button>
                      {isExpanded && (
                        <div className="px-4 pb-4 border-t border-slate-100">
                          <p className="text-xs text-slate-500 mt-3 mb-3">{t.description}</p>
                          {hasParams && (
                            <div className="bg-slate-50 rounded-lg p-3.5">
                              <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-3">Parameters</p>
                              <div className="space-y-2">
                                {Object.entries(t.input_schema.properties).map(([k, v]: [string, any]) => {
                                  const isRequired = t.input_schema.required?.includes(k)
                                  return (
                                    <div key={k} className="flex items-center justify-between text-xs bg-white rounded-md px-3 py-2 border border-slate-100">
                                      <div className="flex items-center gap-2">
                                        <code className="font-mono font-medium text-slate-800">{k}</code>
                                        {isRequired && <span className="text-[10px] text-red-400 font-semibold bg-red-50 px-1.5 py-0.5 rounded">required</span>}
                                      </div>
                                      <span className="text-slate-400 font-mono">{v.type}</span>
                                    </div>
                                  )
                                })}
                              </div>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-xl p-6 lg:p-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-white/10">
              <Puzzle size={17} className="text-emerald-400" />
            </div>
            <h2 className="font-semibold text-white">MCP Connection</h2>
          </div>
          <button
            onClick={copyConfig}
            className="inline-flex items-center gap-1.5 text-xs bg-white/10 hover:bg-white/20 text-white/80 px-3.5 py-2 rounded-lg transition-colors font-medium"
          >
            {copied ? (
              <>
                <CheckCheck size={14} className="text-emerald-400" />
                Copied!
              </>
            ) : (
              <>
                <Copy size={14} />
                Copy config
              </>
            )}
          </button>
        </div>
        <p className="text-xs text-slate-400 mb-4">Add this to your agent&apos;s MCP configuration to start using the generated tools:</p>
        <pre className="bg-black/30 text-emerald-200/80 text-xs leading-relaxed p-5 rounded-xl overflow-x-auto border border-white/5 font-mono">
{`{
  "mcpServers": {
    "agentbridge": {
      "url": "https://agentbridge-demo.onrender.com/mcp/"
    }
  }
}`}
        </pre>
      </div>

      {viewedArtifact && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" onClick={() => { setViewedArtifact(null); setArtifactContent(null) }}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-4xl max-h-[85vh] flex flex-col overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-2 rounded-lg bg-indigo-100">
                  <FileCode2 size={18} className="text-indigo-600" />
                </div>
                <div className="min-w-0">
                  <h3 className="font-semibold text-slate-800 truncate">{viewedArtifact.name}</h3>
                  <p className="text-xs text-slate-400">{viewedArtifact.type} · {viewedArtifact.endpoint_count} endpoints</p>
                </div>
              </div>
              <button
                onClick={() => { setViewedArtifact(null); setArtifactContent(null) }}
                className="p-2 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-6">
              {artifactContent === null ? (
                <div className="flex items-center justify-center py-16">
                  <div className="animate-pulse flex flex-col items-center gap-4">
                    <div className="w-8 h-8 rounded-full bg-slate-200" />
                    <p className="text-sm text-slate-400">Loading content...</p>
                  </div>
                </div>
              ) : (
                <pre className="text-xs leading-relaxed font-mono text-slate-700 whitespace-pre-wrap bg-slate-50 rounded-xl p-5 border border-slate-100 max-h-[60vh] overflow-auto">
                  {artifactContent}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
