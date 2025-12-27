const STORAGE_KEY = 'app_locale'

type SupportedLocale = 'zh' | 'en'

const defaultLocale: SupportedLocale =
  (navigator?.language?.toLowerCase().startsWith('en') ? 'en' : 'zh') as SupportedLocale

let currentLocale: SupportedLocale = (localStorage.getItem(STORAGE_KEY) as SupportedLocale) || defaultLocale

export const getLocale = () => currentLocale

export const setLocale = (lang: SupportedLocale) => {
  currentLocale = lang
  localStorage.setItem(STORAGE_KEY, lang)
  window.dispatchEvent(new CustomEvent('localeChanged', { detail: { lang } }))
}

export const onLocaleChange = (handler: (lang: SupportedLocale) => void) => {
  const listener = (event: Event) => {
    const detail = (event as CustomEvent).detail
    handler(detail?.lang || currentLocale)
  }
  window.addEventListener('localeChanged', listener)
  return () => window.removeEventListener('localeChanged', listener)
}

export type { SupportedLocale }

