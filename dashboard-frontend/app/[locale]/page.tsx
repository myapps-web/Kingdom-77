import { useTranslations } from 'next-intl';
import LanguageSwitcher from '@/components/LanguageSwitcher';
import Link from 'next/link';

export default function Home() {
  const t = useTranslations();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      {/* Header */}
      <header className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">K77</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">
                {t('common.brand')}
              </span>
            </div>
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              <Link
                href="/dashboard"
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                {t('common.login')}
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center space-y-8">
          <div className="space-y-4">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 dark:text-white">
              {t('home.title')}
            </h1>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              {t('home.subtitle')}
            </p>
          </div>

          <div className="flex gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-8 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              {t('home.getStarted')}
            </Link>
            <Link
              href="/documentation"
              className="px-8 py-3 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 rounded-lg font-medium transition-colors"
            >
              {t('home.documentation')}
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            {
              key: 'moderation',
              icon: '🛡️',
            },
            {
              key: 'leveling',
              icon: '📊',
            },
            {
              key: 'tickets',
              icon: '🎫',
            },
            {
              key: 'premium',
              icon: '⭐',
            },
          ].map((feature) => (
            <div
              key={feature.key}
              className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-shadow"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {t(`home.features.${feature.key}.title`)}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {t(`home.features.${feature.key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p>{t('footer.copyright')}</p>
            <div className="flex gap-6 justify-center mt-4">
              <Link href="/privacy" className="hover:text-blue-600 dark:hover:text-blue-400">
                {t('footer.links.privacy')}
              </Link>
              <Link href="/terms" className="hover:text-blue-600 dark:hover:text-blue-400">
                {t('footer.links.terms')}
              </Link>
              <Link href="/contact" className="hover:text-blue-600 dark:hover:text-blue-400">
                {t('footer.links.contact')}
              </Link>
              <Link href="/documentation" className="hover:text-blue-600 dark:hover:text-blue-400">
                {t('footer.links.documentation')}
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
