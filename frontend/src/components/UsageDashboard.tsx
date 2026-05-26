import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { useI18n } from '../i18n/context'
import { fetchUsage, fetchUsageCount } from '../lib/api'
import { Activity, TrendingUp } from 'lucide-react'

interface UsageDay {
  date: string
  count: number
}

export default function UsageDashboard() {
  const { t } = useI18n()
  const [usage, setUsage] = useState<UsageDay[]>([])
  const [countData, setCountData] = useState<{ total: number; limit: number; remaining: number } | null>(null)

  useEffect(() => {
    fetchUsage(30).then(setUsage).catch(() => setUsage([]))
    fetchUsageCount().then(setCountData).catch(() => {})
  }, [])

  const total = usage.reduce((sum, d) => sum + d.count, 0)
  const limit = countData?.limit || 0
  const pct = limit > 0 ? Math.min((countData?.total || 0) / limit * 100, 100) : 0

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="mb-10">
        <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{t('usage.title')}</h1>
        <p className="text-sm text-slate-500 mt-1.5">{t('usage.subtitle')}</p>
      </div>

      {countData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-emerald-100">
                <Activity size={20} className="text-emerald-600" />
              </div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{t('usage.today')}</p>
            </div>
            <p className="text-3xl font-bold text-slate-900">{usage.length > 0 ? usage[usage.length - 1]?.count || 0 : 0}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-indigo-100">
                <TrendingUp size={20} className="text-indigo-600" />
              </div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{t('usage.total')}</p>
            </div>
            <p className="text-3xl font-bold text-slate-900">{total}</p>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6"
          >
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2.5 rounded-xl bg-amber-100">
                <Activity size={20} className="text-amber-600" />
              </div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{t('usage.remaining')}</p>
            </div>
            <p className="text-3xl font-bold text-slate-900">{countData.remaining}</p>
          </motion.div>
        </div>
      )}

      {limit > 0 && (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-slate-700">{t('usage.endpointCalls')}</h3>
            <span className="text-xs text-slate-400">
              {countData?.total || 0} {t('usage.ofLimit', { limit })}
            </span>
          </div>
          <div className="w-full h-3 rounded-full bg-slate-100 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${pct}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className={`h-full rounded-full ${
                pct > 80 ? 'bg-gradient-to-r from-amber-500 to-red-500' : 'bg-gradient-to-r from-indigo-500 to-purple-600'
              }`}
            />
          </div>
        </div>
      )}

      <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6">
        <h3 className="text-lg font-semibold text-slate-800 mb-6">{t('usage.daily')}</h3>
        {usage.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-sm text-slate-400">{t('usage.noData')}</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={usage}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis
                dataKey="date"
                tick={{ fontSize: 11, fill: '#94a3b8' }}
                tickFormatter={(v: string) => {
                  const d = new Date(v)
                  return `${d.getMonth() + 1}/${d.getDate()}`
                }}
              />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} allowDecimals={false} />
              <Tooltip
                contentStyle={{
                  background: '#1e293b',
                  border: 'none',
                  borderRadius: '12px',
                  color: '#f1f5f9',
                  fontSize: '12px',
                }}
                formatter={(value: number) => [value, t('usage.endpointCalls')]}
                labelFormatter={(label: string) => {
                  const d = new Date(label)
                  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                }}
              />
              <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  )
}
