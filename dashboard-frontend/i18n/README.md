# Dashboard Internationalization (i18n)

Multi-language support for Kingdom-77 Dashboard using next-intl.

## Supported Languages

- 🇺🇸 **English (en)** - Default
- 🇸🇦 **Arabic (ar)** - RTL support
- 🇪🇸 **Spanish (es)**
- 🇫🇷 **French (fr)**
- 🇩🇪 **German (de)**

## Structure

```
i18n/
├── config.ts           # Language configuration
├── request.ts          # Server-side request handler
└── messages/
    ├── en.json         # English translations
    ├── ar.json         # Arabic translations (RTL)
    ├── es.json         # Spanish translations
    ├── fr.json         # French translations
    └── de.json         # German translations
```

## Usage

### In Server Components

```tsx
import { useTranslations } from 'next-intl';

export default function ServerComponent() {
  const t = useTranslations();
  
  return (
    <div>
      <h1>{t('home.title')}</h1>
      <p>{t('home.subtitle')}</p>
    </div>
  );
}
```

### In Client Components

```tsx
'use client';

import { useTranslations } from 'next-intl';

export default function ClientComponent() {
  const t = useTranslations('common');
  
  return (
    <button>{t('save')}</button>
  );
}
```

### Language Switcher

```tsx
import LanguageSwitcher from '@/components/LanguageSwitcher';

<LanguageSwitcher />
```

## Translation Keys

All translation keys are nested in JSON format:

```json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel"
  },
  "dashboard": {
    "title": "Dashboard",
    "overview": "Overview"
  }
}
```

Access with dot notation: `t('common.save')` or `t('dashboard.title')`

## RTL Support

Arabic language automatically applies RTL (right-to-left) layout:

- Text direction: `dir="rtl"`
- Text alignment: `text-align: right`
- Reversed flex directions

## Adding New Languages

1. Add language code to `i18n/config.ts`:
```ts
export const locales = ['en', 'ar', 'es', 'fr', 'de', 'ja'] as const;
export type Locale = (typeof locales)[number];
```

2. Add language name and flag:
```ts
export const localeNames: Record<Locale, string> = {
  // ... existing languages
  ja: '日本語',
};

export const localeFlags: Record<Locale, string> = {
  // ... existing flags
  ja: '🇯🇵',
};
```

3. Create translation file: `i18n/messages/ja.json`

4. Copy structure from `en.json` and translate all keys

## URL Structure

All routes are prefixed with locale:

- English: `/en/dashboard`
- Arabic: `/ar/dashboard`
- Spanish: `/es/dashboard`
- French: `/fr/dashboard`
- German: `/de/dashboard`

The middleware automatically detects browser language and redirects.

## Translation Coverage

### Common (18 keys)
- UI elements (buttons, labels)
- Form actions
- Navigation items

### Navigation (10 keys)
- Dashboard sections
- Settings
- Support

### Home Page (20+ keys)
- Hero section
- Features
- Call-to-actions

### Dashboard (30+ keys)
- Statistics
- Quick actions
- Server overview

### Moderation (25+ keys)
- Logs
- Settings
- Actions

### Leveling (20+ keys)
- Leaderboard
- Settings
- Rewards

### Tickets (25+ keys)
- Categories
- Settings
- Active tickets

### Premium (30+ keys)
- Features
- Pricing
- Trial information

### Settings (25+ keys)
- Profile
- Appearance
- Notifications
- Security

### Auth (15+ keys)
- Login/Signup
- Errors

### Footer (5 keys)
- Copyright
- Links

**Total: 150+ translation keys per language**

## Testing

Test language switching:

1. Click language switcher in header
2. Select different language
3. Verify page reloads with new language
4. Check URL contains correct locale prefix
5. For Arabic, verify RTL layout

## Best Practices

1. **Never hardcode text** - Always use translation keys
2. **Keep keys organized** - Group related translations
3. **Use descriptive keys** - `dashboard.statistics.members` not `stat1`
4. **Add placeholders** - Use `{variable}` for dynamic content
5. **Test all languages** - Ensure translations make sense in context
6. **Consider length** - Some languages are longer (German) or shorter (Chinese)
7. **RTL awareness** - Test Arabic layout thoroughly

## Development

### Adding New Translation Keys

1. Add key to `en.json` (source of truth)
2. Add same key to all other language files
3. Translate the value appropriately
4. Use in components with `t('your.new.key')`

### Translation Variables

Use curly braces for dynamic content:

```json
{
  "welcome": "Welcome, {name}!"
}
```

```tsx
t('welcome', { name: userName })
```

## Production Deployment

1. All translations are bundled at build time
2. No runtime translation needed
3. Static pages are generated for each locale
4. Fast page loads with pre-rendered content

## Integration with Backend

The dashboard language preference can sync with the bot's language system:

1. User selects language in dashboard
2. Save to `user_language_preferences` collection in MongoDB
3. Bot reads preference when user interacts
4. Consistent experience across bot and dashboard
