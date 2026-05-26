import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useI18n } from '../i18n/context'
import { fetchMe, fetchUsage, fetchUsageCount } from '../lib/api'
import {
  Activity,
  TrendingUp,
  Users,
  CreditCard,
  ArrowRight,
  Zap,
  Crown,
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function ProDashboard() {
  const { t } = useI18n()
  const [user, setUser] = useState<{ tier: string; email: string; display_name: string | null } | null>(null)
  const [usage, setUsage] = useState<Array<{ date: string; count: number }>>([])
  const [countData, setCountData] = useState<{ total: number; limit: number; remaining: number } | null>(null)

  useEffect(() => {
    fetchMe().then(setUser).catch(() => {})
    fetchUsage(7).then(setUsage).catch(() => setUsage([]))
    fetchUsageCount().then(setCountData).catch(() => {})
  }, [])

  const tier = user?.tier || 'free'
  const isPaid = tier !== 'free'
  const limit = countData?.limit || 0
  const pct = limit > 0 ? Math.min((countData?.total || 0) / limit * 100, 100) : 0

  const quickLinks = [
    { to: '/billing', label: t('nav.billing'), icon: CreditCard, gradient: 'from-amber-500 to-orange-600', accent: 'bg-amber-500/10 text-amber-600' },
    { to: '/teams', label: t('nav.teams'), icon: Users, gradient: 'from-emerald-500 to-teal-600', accent: 'bg-emerald-500/10 text-emerald-600' },
    { to: '/usage', label: t('nav.usage'), icon: Activity, gradient: 'from-violet-500 to-indigo-600', accent: 'bg-violet-500/10 text-violet-600' },
    { to: '/api-keys', label: t('nav.apiKeys'), icon: Zap, gradient: 'from-rose-500 to-pink-600', accent: 'bg-rose-500/10 text-rose-600' },
  ]

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-10">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest">AgentBridge</p>
            {isPaid && (
              <span className={`inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-1 rounded-full ${
                tier === 'enterprise'
                  ? 'bg-purple-100 text-purple-700 border border-purple-200'
                  : 'bg-amber-100 text-amber-700 border border-amber-200'
              }`}>
                {tier === 'enterprise' ? <Crown size={10} /> : <Zap size={10} />}
                {t(`upgrade.${tier}Badge`)}
              </span>
            )}
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            {user?.display_name ? `Welcome back, ${user.display_name}` : t('nav.dashboard')}
          </h1>
          <p className="text-sm text-slate-500 mt-1.5">Your API bridge activity overview</p>
        </div>
      </div>

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
                pct > 80 ? 'bg-gradient-to-r from-amber-500 to-red-500' :
                pct > 50 ? 'bg-gradient-to-r from-indigo-500 to-violet-500' :
                'bg-gradient-to-r from-emerald-500 to-teal-500'
              }`}
            />
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {quickLinks.map((link, i) => {
          const Icon = link.icon
          return (
            <motion.div
              key={link.to}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <Link
                to={link.to}
                className="group relative overflow-hidden rounded-2xl bg-white border border-slate-200/60 p-5 hover:shadow-lg hover:border-slate-300 transition-all duration-300 block"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-2.5 rounded-xl ${link.accent.split(' ')[0]}`}>
                    <Icon size={22} className={link.accent.split(' ')[1]} />
                  </div>
                  <div className={`h-1 w-8 rounded-full bg-gradient-to-r ${link.gradient} opacity-0 group-hover:opacity-100 group-hover:w-12 transition-all duration-500`} />
                </div>
                <p className="font-semibold text-slate-800">{link.label}</p>
                <div className="flex items-center gap-1 mt-2 text-xs text-slate-400 group-hover:text-indigo-600 transition-colors">
                  Manage <ArrowRight size={10} />
                </div>
              </Link>
            </motion.div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold text-slate-800">{t('usage.daily')}</h3>
            <span className="text-xs text-slate-400">{t('usage.last7days')}</span>
          </div>
          {usage.length === 0 ? (
            <div className="text-center py-12">
              <TrendingUp size={40} className="mx-auto text-slate-300 mb-3" />
              <p className="text-sm text-slate-400">{t('usage.noData')}</p>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={260}>
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
                  contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '12px', color: '#f1f5f9', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="bg-gradient-to-br from-indigo-50 to-violet-50 rounded-2xl border border-indigo-100 p-6">
          <div className="flex gap-3 mb-4">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
              <Zap size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-semibold text-indigo-800 mb-1">
                {isPaid ? `${t(`upgrade.${tier}Badge`)} Features Active` : 'Free Tier'}
              </p>
              <p className="text-xs text-indigo-600 leading-relaxed">
                {isPaid
                  ? tier === 'enterprise'
                    ? 'Unlimited everything + SSO, audit logs, and priority support.'
                    : '50 endpoints, 5 teams, private MCP, and custom branding.'
                  : '3 endpoints, 1 team. Upgrade to unlock more features.'}
              </p>
            </div>
          </div>
          {!isPaid && (
            <Link
              to="/billing"
              className="inline-flex items-center gap-1.5 text-xs text-indigo-700 hover:text-indigo-800 font-semibold transition-colors"
            >
              {t('upgrade.cta')} <ArrowRight size={11} />
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
