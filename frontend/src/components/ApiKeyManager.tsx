import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useI18n } from '../i18n/context'
import { fetchMe, generateApiKey, revokeApiKey, regenerateApiKey, setApiKey as saveApiKey } from '../lib/api'
import { Key, Copy, CheckCheck, Trash2, RefreshCw } from 'lucide-react'

export default function ApiKeyManager() {
  const { t } = useI18n()
  const [user, setUser] = useState<{ api_key: string | null } | null>(null)
  const [apiKey, setApiKey] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchMe().then(setUser).catch(() => {})
  }, [])

  const handleGenerate = async () => {
    setLoading(true)
    try {
      const data = await generateApiKey()
      setApiKey(data.api_key)
      saveApiKey(data.api_key)
      setUser(s => s ? { ...s, api_key: data.api_key } : null)
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleRevoke = async () => {
    setLoading(true)
    try {
      await revokeApiKey()
      setApiKey(null)
      setUser(s => s ? { ...s, api_key: null } : null)
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleRegenerate = async () => {
    setLoading(true)
    try {
      const data = await regenerateApiKey()
      setApiKey(data.api_key)
      saveApiKey(data.api_key)
      setUser(s => s ? { ...s, api_key: data.api_key } : null)
    } catch { /* ignore */ }
    setLoading(false)
  }

  const handleCopy = async (key: string) => {
    await navigator.clipboard.writeText(key)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const hasKey = !!(apiKey || user?.api_key)
  const displayKey = apiKey || user?.api_key

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="mb-10">
        <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{t('apiKeys.title')}</h1>
        <p className="text-sm text-slate-500 mt-1.5">{t('apiKeys.subtitle')}</p>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 lg:p-8"
      >
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 rounded-xl bg-indigo-100">
            <Key size={24} className="text-indigo-600" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-slate-800">API Key</h2>
            <p className="text-sm text-slate-500">{t('apiKeys.usage')}</p>
          </div>
        </div>

        {hasKey ? (
          <div className="space-y-4">
            <div className="bg-slate-900 rounded-xl p-5 border border-slate-700">
              <div className="flex items-center justify-between gap-4 mb-2">
                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest">API Key</p>
                <button
                  onClick={() => handleCopy(displayKey!)}
                  className="inline-flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-400 transition-colors"
                >
                  {copied ? (
                    <>
                      <CheckCheck size={14} className="text-emerald-400" />
                      <span className="text-emerald-400">{t('apiKeys.copied')}</span>
                    </>
                  ) : (
                    <>
                      <Copy size={14} />
                      {t('apiKeys.copy')}
                    </>
                  )}
                </button>
              </div>
              <code className="text-sm font-mono text-emerald-300 break-all">
                {displayKey}
              </code>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={handleRegenerate}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-indigo-50 text-indigo-700 hover:bg-indigo-100 transition-colors"
              >
                <RefreshCw size={15} />
                {t('apiKeys.regenerate')}
              </button>
              <button
                onClick={handleRevoke}
                disabled={loading}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
              >
                <Trash2 size={15} />
                {t('apiKeys.revoke')}
              </button>
            </div>
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="w-16 h-16 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-4">
              <Key size={28} className="text-slate-400" />
            </div>
            <p className="text-sm text-slate-500 mb-6">{t('apiKeys.noKey')}</p>
            <button
              onClick={handleGenerate}
              disabled={loading}
              className="inline-flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-600/25 disabled:opacity-50"
            >
              <Key size={16} />
              {t('apiKeys.generate')}
            </button>
          </div>
        )}
      </motion.div>

      {apiKey && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 bg-amber-50 border border-amber-200 rounded-xl p-4"
        >
          <p className="text-sm text-amber-700">
            {t('apiKeys.generateWarning')}
          </p>
        </motion.div>
      )}
    </div>
  )
}
