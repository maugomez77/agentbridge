import { motion, AnimatePresence } from 'framer-motion'
import { useI18n } from '../i18n/context'
import { X, Sparkles, ArrowRight, Shield, Brush, Lock, TrendingUp } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface Props {
  open: boolean
  onClose: () => void
  current: number
  maxLimit: number
}

export default function UpgradeModal({ open, onClose, current, maxLimit }: Props) {
  const { t } = useI18n()
  const navigate = useNavigate()

  const handleUpgrade = () => {
    onClose()
    navigate('/billing')
  }

  return (
    <AnimatePresence>
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden"
          >
            <div className="bg-gradient-to-br from-indigo-500 via-purple-600 to-indigo-700 p-6">
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-1.5 rounded-lg bg-white/20 hover:bg-white/30 text-white transition-colors"
              >
                <X size={16} />
              </button>
              <div className="text-center">
                <div className="w-14 h-14 rounded-2xl bg-white/20 flex items-center justify-center mx-auto mb-4 backdrop-blur-sm">
                  <Sparkles size={28} className="text-amber-300" />
                </div>
                <h2 className="text-xl font-bold text-white mb-1">{t('upgrade.title')}</h2>
                <p className="text-sm text-indigo-200">
                  {t('upgrade.endpointLimit', { current, limit: maxLimit })}
                </p>
              </div>
            </div>

            <div className="p-6">
              <div className="grid grid-cols-2 gap-3 mb-6">
                <div className="flex items-center gap-2 text-sm">
                  <Shield size={16} className="text-indigo-500 flex-shrink-0" />
                  <span className="text-slate-600">Unlimited endpoints</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Brush size={16} className="text-purple-500 flex-shrink-0" />
                  <span className="text-slate-600">Custom branding</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Lock size={16} className="text-emerald-500 flex-shrink-0" />
                  <span className="text-slate-600">Private MCP</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <TrendingUp size={16} className="text-amber-500 flex-shrink-0" />
                  <span className="text-slate-600">5 teams</span>
                </div>
              </div>

              <button
                onClick={handleUpgrade}
                className="w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3.5 rounded-xl text-sm font-bold hover:from-indigo-700 hover:to-purple-700 transition-all shadow-lg shadow-indigo-500/25"
              >
                {t('upgrade.cta')}
                <ArrowRight size={16} />
              </button>
              <p className="text-center text-xs text-slate-400 mt-3">
                Starting at $29/month. Cancel anytime.
              </p>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  )
}
