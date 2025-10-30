import createMiddleware from 'next-intl/middleware';
import { locales, defaultLocale } from './i18n/config';

export default createMiddleware({
  // A list of all locales that are supported
  locales,

  // Used when no locale matches
  defaultLocale,

  // Automatically detect locale from browser headers
  localeDetection: true,

  // Prefix the default locale in the URL (e.g., /en/dashboard)
  localePrefix: 'always',
});

export const config = {
  // Match all pathnames except for
  // - API routes
  // - _next (Next.js internals)
  // - files with extensions (e.g. .png, .css)
  matcher: ['/((?!api|_next|.*\\..*).*)'],
};
