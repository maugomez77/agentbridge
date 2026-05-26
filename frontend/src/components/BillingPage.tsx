import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { useI18n } from '../i18n/context'
import { fetchTiers, fetchSubscription, upgradeTier, downgradeTier, cancelSubscription, reactivateSubscription } from '../lib/api'

interface Tier {
  tier: string
  price_monthly: number
  price_yearly: number
  endpoints: number
  teams: number
  features: string[]
  highlighted: boolean
}

export default function BillingPage() {
  const { t } = useI18n()
  const [tiers, setTiers] = useState<Tier[]>([])
  const [subscription, setSubscription] = useState<{ tier: string; cancel_at_period_end: boolean; current_period_end: string | null } | null>(null)
  const [isYearly, setIsYearly] = useState(false)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchTiers().then(setTiers).catch(() => {})
    fetchSubscription().then(setSubscription).catch(() => {})
  }, [])

  const handleUpgrade = async (tier: string) => {
    setLoading(true)
    try {
      const result = await upgradeTier(tier)
      setSubscription({
        tier: result.tier,
        cancel_at_period_end: false,
        current_period_end: null,
      })
    } catch { /* handled */ }
    setLoading(false)
  }

  const handleDowngrade = async () => {
    setLoading(true)
    try {
      await downgradeTier()
      setSubscription({ tier: 'free', cancel_at_period_end: false, current_period_end: null })
    } catch { /* handled */ }
    setLoading(false)
  }

  const handleCancel = async () => {
    setLoading(true)
    try {
      await cancelSubscription()
      setSubscription(s => s ? { ...s, cancel_at_period_end: true } : null)
    } catch { /* handled */ }
    setLoading(false)
  }

  const handleReactivate = async () => {
    setLoading(true)
    try {
      await reactivateSubscription()
      setSubscription(s => s ? { ...s, cancel_at_period_end: false } : null)
    } catch { /* handled */ }
    setLoading(false)
  }

  const currentTier = subscription?.tier || 'free'

  return (
    <div className="p-6 lg:p-10 max-w-7xl mx-auto">
      <div className="mb-10">
        <p className="text-xs font-medium text-indigo-500 uppercase tracking-widest mb-2">AgentBridge</p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">{t('billing.title')}</h1>
        <p className="text-sm text-slate-500 mt-1.5">{t('billing.subtitle')}</p>
      </div>

      {subscription && (
        <div className="bg-white rounded-2xl border border-slate-200/60 shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div>
              <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1">{t('billing.current')}</p>
              <div className="flex items-center gap-3">
                <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-bold ${
                  currentTier === 'enterprise'
                    ? 'bg-purple-100 text-purple-700'
                    : currentTier === 'pro'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-slate-100 text-slate-600'
                }`}>
                  {currentTier === 'pro' && <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />}
                  {currentTier === 'enterprise' && <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />}
                  {t(`billing.${currentTier}`)}
                </span>
                {subscription.cancel_at_period_end && (
                  <span className="text-xs text-amber-600 bg-amber-50 px-2 py-1 rounded-lg font-medium">
                    Cancels at period end
                  </span>
                )}
              </div>
            </div>
            {currentTier !== 'free' && (
              <div className="flex items-center gap-3">
                {subscription.cancel_at_period_end ? (
                  <button
                    onClick={handleReactivate}
                    disabled={loading}
                    className="px-4 py-2 rounded-xl text-sm font-semibold bg-emerald-100 text-emerald-700 hover:bg-emerald-200 transition-colors"
                  >
                    {t('billing.reactivate')}
                  </button>
                ) : (
                  <button
                    onClick={handleCancel}
                    disabled={loading}
                    className="px-4 py-2 rounded-xl text-sm font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                  >
                    {t('billing.cancel')}
                  </button>
                )}
                <button
                  onClick={handleDowngrade}
                  disabled={loading}
                  className="px-4 py-2 rounded-xl text-sm font-semibold bg-red-50 text-red-600 hover:bg-red-100 transition-colors"
                >
                  {t('billing.downgrade')}
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="flex items-center justify-center mb-8">
        <div className="bg-slate-100 rounded-xl p-1 inline-flex items-center">
          <button
            onClick={() => setIsYearly(false)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${!isYearly ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500'}`}
          >
            Monthly
          </button>
          <button
            onClick={() => setIsYearly(true)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${isYearly ? 'bg-white shadow-sm text-slate-900' : 'text-slate-500'}`}
          >
            Yearly
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {tiers.map((tier) => {
          const isCurrent = currentTier === tier.tier
          const price = isYearly ? tier.price_yearly : tier.price_monthly
          const perLabel = isYearly ? t('billing.year') : t('billing.month')

          return (
            <motion.div
              key={tier.tier}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: tier.tier === 'free' ? 0 : tier.tier === 'pro' ? 0.1 : 0.2 }}
              className={`relative rounded-2xl border-2 p-6 transition-all ${
                tier.highlighted
                  ? 'border-indigo-500 shadow-lg shadow-indigo-500/10 bg-white ring-1 ring-indigo-500/20'
                  : 'border-slate-200 bg-white shadow-sm hover:border-slate-300'
              }`}
            >
              {tier.highlighted && (
                <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs font-bold px-4 py-1 rounded-full shadow-md">
                  {t('billing.popular')}
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-lg font-bold text-slate-800 capitalize">{t(`billing.${tier.tier}`)}</h3>
                <div className="mt-3">
                  <span className="text-4xl font-extrabold text-slate-900">${price}</span>
                  <span className="text-sm text-slate-400 ml-1">{perLabel}</span>
                </div>
                {isYearly && price > 0 && (
                  <p className="text-xs text-emerald-600 font-medium mt-1">{t('billing.saveYearly', { amount: tier.price_monthly * 2 })}</p>
                )}
              </div>

              <div className="space-y-3 mb-6">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{t('billing.endpoints')}</span>
                  <span className="font-bold text-slate-800">{tier.endpoints === 999999 ? 'Unlimited' : tier.endpoints}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-slate-600">{t('billing.teams')}</span>
                  <span className="font-bold text-slate-800">{tier.teams === 999999 ? 'Unlimited' : tier.teams}</span>
                </div>
                <div className="border-t border-slate-100 pt-3 space-y-2">
                  {tier.features.map((f, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm text-slate-600">
                      <svg className="w-4 h-4 text-emerald-500 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {f}
                    </div>
                  ))}
                </div>
              </div>

              <button
                onClick={() => handleUpgrade(tier.tier)}
                disabled={isCurrent || loading}
                className={`w-full py-3 rounded-xl text-sm font-bold transition-all ${
                  isCurrent
                    ? 'bg-slate-100 text-slate-400 cursor-default'
                    : tier.highlighted
                    ? 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-lg shadow-indigo-600/25'
                    : 'bg-slate-800 text-white hover:bg-slate-900'
                }`}
              >
                {isCurrent ? t('billing.currentPlan') : t('billing.upgrade')}
              </button>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
