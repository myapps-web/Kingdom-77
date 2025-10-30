/**
 * i18n Configuration for Kingdom-77 Dashboard
 * Supports 5 languages: EN, AR, ES, FR, DE
 */

export type Locale = 'en' | 'ar' | 'es' | 'fr' | 'de';

export const locales: Locale[] = ['en', 'ar', 'es', 'fr', 'de'];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, string> = {
  en: 'English',
  ar: 'العربية',
  es: 'Español',
  fr: 'Français',
  de: 'Deutsch',
};

export const localeFlags: Record<Locale, string> = {
  en: '🇺🇸',
  ar: '🇸🇦',
  es: '🇪🇸',
  fr: '🇫🇷',
  de: '🇩🇪',
};

export const rtlLocales: Locale[] = ['ar'];

export function isRTL(locale: Locale): boolean {
  return rtlLocales.includes(locale);
}

export function getLocaleDirection(locale: Locale): 'ltr' | 'rtl' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}
