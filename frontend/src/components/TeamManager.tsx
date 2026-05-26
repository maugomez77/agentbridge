import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useI18n } from '../i18n/context'
import { fetchTeams, createTeam, deleteTeam, addTeamMember, removeTeamMember } from '../lib/api'
import { Users, Plus, X, UserPlus } from 'lucide-react'

interface Team {
  id: string
  name: string
  owner_id: string
  member_ids: string[]
  created_at: string
}

export default function TeamManager() {
  const { t } = useI18n()
  const [teams, setTeams] = useState<Team[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [addEmail, setAddEmail] = useState('')
  const [activeTeam, setActiveTeam] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const load = () => {
    fetchTeams().then(setTeams).catch(() => setTeams([]))
  }

  useEffect(() => { load() }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newName.trim()) return
    setLoading(true)
    try {
      await createTeam(newName.trim())
      setNewName('')
      setShowCreate(false)
      load()
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleDelete = async (teamId: string) => {
    setLoading(true)
    try {
      await deleteTeam(teamId)
      load()
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleAddMember = async (teamId: string) => {
    if (!addEmail.trim()) return
    setLoading(true)
    try {
      await addTeamMember(teamId, addEmail.trim())
      setAddEmail('')
      load()
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleRemoveMember = async (teamId: string, memberId: string) => {
    setLoading(true)
    try {
      await removeTeamMember(teamId, memberId)
      load()
    } catch { /* ignore */ }
    setLoading(false)
  }

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
        <div>
          <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">{t('teams.title')}</h1>
          <p className="text-sm text-slate-500 mt-1.5">{t('teams.subtitle')}</p>
        </div>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className={`inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
            showCreate
              ? 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-600/25'
          }`}
        >
          {showCreate ? <X size={16} /> : <Plus size={16} />}
          {showCreate ? t('common.cancel') : t('teams.create')}
        </button>
      </div>

      {showCreate && (
        <motion.form
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          onSubmit={handleCreate}
          className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 mb-8"
        >
          <div className="flex items-end gap-4">
            <div className="flex-1">
              <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{t('teams.name')}</label>
              <input
                value={newName}
                onChange={e => setNewName(e.target.value)}
                className="w-full border border-slate-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all bg-slate-50 focus:bg-white"
                placeholder="My Team"
                required
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="bg-indigo-600 text-white px-5 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-sm disabled:opacity-50"
            >
              {t('teams.create')}
            </button>
          </div>
        </motion.form>
      )}

      {teams.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-16 text-center">
          <div className="w-16 h-16 rounded-2xl bg-indigo-50 flex items-center justify-center mx-auto mb-5">
            <Users size={32} className="text-indigo-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-700 mb-2">{t('teams.noTeams')}</h3>
          <p className="text-sm text-slate-400 max-w-sm mx-auto mb-8">{t('teams.subtitle')}</p>
          <button
            onClick={() => setShowCreate(true)}
            className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/25"
          >
            <Plus size={18} />
            {t('teams.create')}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {teams.map(team => (
            <motion.div
              key={team.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md">
                    {team.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-slate-800">{team.name}</h3>
                    <p className="text-xs text-slate-400">{team.member_ids.length + 1} {t('teams.members').toLowerCase()}</p>
                  </div>
                </div>
                <button
                  onClick={() => handleDelete(team.id)}
                  className="p-2 rounded-lg hover:bg-red-50 text-slate-400 hover:text-red-500 transition-colors"
                >
                  <X size={16} />
                </button>
              </div>

              {activeTeam === team.id && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="border-t border-slate-100 pt-4 mt-2"
                >
                  <div className="flex items-end gap-3 mb-4">
                    <div className="flex-1">
                      <label className="block text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1">{t('teams.addMember')}</label>
                      <input
                        value={addEmail}
                        onChange={e => setAddEmail(e.target.value)}
                        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                        placeholder="user@example.com"
                      />
                    </div>
                    <button
                      onClick={() => handleAddMember(team.id)}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-indigo-700 transition-colors"
                    >
                      <UserPlus size={14} />
                    </button>
                  </div>

                  {team.member_ids.length > 0 && (
                    <div className="space-y-2">
                      {team.member_ids.map(mid => (
                        <div key={mid} className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-50">
                          <span className="text-sm text-slate-600 font-mono">{mid}</span>
                          <button
                            onClick={() => handleRemoveMember(team.id, mid)}
                            className="text-xs text-red-400 hover:text-red-600 font-medium"
                          >
                            {t('teams.remove')}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}

              <button
                onClick={() => setActiveTeam(activeTeam === team.id ? null : team.id)}
                className="mt-4 text-xs text-indigo-600 hover:text-indigo-700 font-semibold transition-colors"
              >
                {activeTeam === team.id ? t('common.close') : t('teams.addMember')}
              </button>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}
