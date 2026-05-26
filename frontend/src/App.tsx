import { useState, useEffect, useCallback } from 'react'
import { Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard,
  FolderKanban,
  FileCode2,
  Cable,
  CreditCard,
  Users,
  Activity,
  Key,
  LogOut,
  LogIn,
  UserPlus,
  Globe,
  Zap,
  Crown,
  ChevronDown,
} from 'lucide-react'
import { useI18n } from './i18n/context'
import { fetchMe, removeToken } from './lib/api'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Artifacts from './pages/Artifacts'
import LoginPage from './components/LoginPage'
import RegisterPage from './components/RegisterPage'
import BillingPage from './components/BillingPage'
import TeamManager from './components/TeamManager'
import UsageDashboard from './components/UsageDashboard'
import ApiKeyManager from './components/ApiKeyManager'
import ProDashboard from './components/ProDashboard'

interface UserData {
  id: string
  email: string
  display_name: string | null
  tier: string
  api_key: string | null
  created_at: string
}

export default function App() {
  const { t, lang, setLang } = useI18n()
  const loc = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState<UserData | null>(null)
  const [loaded, setLoaded] = useState(false)
  const [showLangMenu, setShowLangMenu] = useState(false)

  useEffect(() => {
    fetchMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoaded(true))
  }, [])

  const handleLogout = useCallback(() => {
    removeToken()
    setUser(null)
    navigate('/')
  }, [navigate])

  const isAuthPage = loc.pathname === '/login' || loc.pathname === '/register'
  const isPaid = user?.tier !== 'free'

  if (!loaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-600 rounded-full animate-spin" />
      </div>
    )
  }

  if (isAuthPage) {
    return (
      <div>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
        </Routes>
      </div>
    )
  }

  const isLoggedIn = !!user

  const baseNavItems = [
    { to: '/', label: t('nav.dashboard'), icon: LayoutDashboard },
    { to: '/projects', label: t('nav.projects'), icon: FolderKanban },
    { to: '/artifacts', label: t('nav.artifacts'), icon: FileCode2 },
  ]

  const proNavItems = isLoggedIn ? [
    { to: '/billing', label: t('nav.billing'), icon: CreditCard },
    { to: '/teams', label: t('nav.teams'), icon: Users },
    { to: '/usage', label: t('nav.usage'), icon: Activity },
    { to: '/api-keys', label: t('nav.apiKeys'), icon: Key },
  ] : []

  const navItems = [...baseNavItems, ...proNavItems]

  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-60 bg-slate-900 flex-shrink-0 flex flex-col min-h-screen sticky top-0">
        <div className="px-5 pt-6 pb-4">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-indigo-500/25">s</div>
            <span className="text-white font-semibold text-base tracking-tight">agentbridge</span>
          </Link>
        </div>

        {isLoggedIn && (
          <div className="px-3 pb-5">
            <Link to="/" className="block bg-slate-800 rounded-xl p-3 hover:bg-slate-700 transition-colors">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-400 to-indigo-600 flex items-center justify-center text-white font-bold text-xs shadow-sm">
                  {user?.display_name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || '?'}
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-white truncate">{user?.display_name || user?.email}</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    {isPaid ? (
                      <span className={`inline-flex items-center gap-0.5 text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        user?.tier === 'enterprise'
                          ? 'bg-purple-500/20 text-purple-300'
                          : 'bg-amber-500/20 text-amber-300'
                      }`}>
                        {user?.tier === 'enterprise' ? <Crown size={9} /> : <Zap size={9} />}
                        {user?.tier === 'enterprise' ? t('upgrade.enterpriseBadge') : t('upgrade.proBadge')}
                      </span>
                    ) : (
                      <span className="text-[10px] text-slate-500">Free</span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          </div>
        )}

        <nav className="flex-1 px-3 space-y-1">
          {navItems.map(item => {
            const Icon = item.icon
            const isActive = loc.pathname === item.to || (item.to !== '/' && loc.pathname.startsWith(item.to))
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-slate-700 text-white shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            )
          })}
        </nav>

        <div className="px-3 py-3 border-t border-slate-800">
          {isLoggedIn ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 w-full text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            >
              <LogOut size={16} />
              {t('auth.signOut')}
            </button>
          ) : (
            <div className="space-y-1">
              <Link
                to="/login"
                className="flex items-center gap-2 px-3 py-2 w-full text-sm text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              >
                <LogIn size={16} />
                {t('auth.loginButton')}
              </Link>
              <Link
                to="/register"
                className="flex items-center gap-2 px-3 py-2 w-full text-sm text-indigo-400 hover:text-indigo-300 hover:bg-slate-800 rounded-lg transition-colors"
              >
                <UserPlus size={16} />
                {t('auth.registerButton')}
              </Link>
            </div>
          )}
        </div>

        <div className="px-3 py-3 border-t border-slate-800 relative">
          <button
            onClick={() => setShowLangMenu(!showLangMenu)}
            className="flex items-center justify-between gap-2 px-3 py-2 w-full text-xs text-slate-500 hover:text-slate-300 rounded-lg transition-colors"
          >
            <div className="flex items-center gap-2">
              <Globe size={14} />
              <span>{lang === 'es' ? 'Español' : 'English'}</span>
            </div>
            <ChevronDown size={12} />
          </button>
          <AnimatePresence>
            {showLangMenu && (
              <motion.div
                initial={{ opacity: 0, y: -5 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -5 }}
                className="absolute bottom-full left-3 right-3 mb-1 bg-slate-800 rounded-lg shadow-xl border border-slate-700 overflow-hidden"
              >
                <button
                  onClick={() => { setLang('en'); setShowLangMenu(false) }}
                  className={`w-full text-left px-3 py-2 text-xs transition-colors ${lang === 'en' ? 'text-white bg-slate-700' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
                >
                  English
                </button>
                <button
                  onClick={() => { setLang('es'); setShowLangMenu(false) }}
                  className={`w-full text-left px-3 py-2 text-xs transition-colors ${lang === 'es' ? 'text-white bg-slate-700' : 'text-slate-400 hover:text-white hover:bg-slate-700'}`}
                >
                  Español
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="px-5 py-3 border-t border-slate-800">
          <div className="flex items-center gap-2 text-xs text-slate-500">
            <Cable size={14} />
            <span>v0.2.0</span>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={isLoggedIn ? <ProDashboard /> : <Dashboard />} />
          <Route path="/projects" element={<Projects />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
          <Route path="/artifacts" element={<Artifacts />} />
          <Route path="/billing" element={<BillingPage />} />
          <Route path="/teams" element={<TeamManager />} />
          <Route path="/usage" element={<UsageDashboard />} />
          <Route path="/api-keys" element={<ApiKeyManager />} />
        </Routes>
      </main>
    </div>
  )
}
