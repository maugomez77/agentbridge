import { createContext, useContext, useState, useCallback, type ReactNode } from 'react'
import en from '../i18n/en.json'
import es from '../i18n/es.json'

type Lang = 'en' | 'es'
type I18nData = typeof en

const translations: Record<Lang, I18nData> = { en, es }

interface I18nContextType {
  lang: Lang
  t: (key: string, vars?: Record<string, string | number>) => string
  setLang: (lang: Lang) => void
}

const I18nContext = createContext<I18nContextType>({
  lang: 'en',
  t: (k: string) => k,
  setLang: () => {},
})

function getNested(obj: Record<string, unknown>, path: string): string {
  const parts = path.split('.')
  let current: unknown = obj
  for (const part of parts) {
    if (current && typeof current === 'object') {
      current = (current as Record<string, unknown>)[part]
    } else {
      return path
    }
  }
  return typeof current === 'string' ? current : path
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>(() => {
    const saved = localStorage.getItem('agentbridge-lang')
    return saved === 'es' ? 'es' : 'en'
  })

  const t = useCallback(
    (key: string, vars?: Record<string, string | number>) => {
      const data = translations[lang]
      let value = getNested(data as unknown as Record<string, unknown>, key)
      if (vars) {
        for (const [k, v] of Object.entries(vars)) {
          value = value.replace(`{{${k}}}`, String(v))
        }
      }
      return value
    },
    [lang],
  )

  const handleSetLang = useCallback((newLang: Lang) => {
    localStorage.setItem('agentbridge-lang', newLang)
    setLang(newLang)
  }, [])

  return <I18nContext.Provider value={{ lang, t, setLang: handleSetLang }}>{children}</I18nContext.Provider>
}

export function useI18n() {
  return useContext(I18nContext)
}
