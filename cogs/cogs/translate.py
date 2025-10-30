"""
Translation Cog - نظام الترجمة التفاعلية
Kingdom-77 Bot v3.6

الميزات:
- Context Menu: Translate Message
- الترجمة حسب لغة الرتبة
- دعم متعدد اللغات
- نظام Cache للترجمات
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from deep_translator import GoogleTranslator
from langdetect import detect

from database import get_db

logger = logging.getLogger(__name__)


# Translation cache
translation_cache = {}
CACHE_MAX_SIZE = 10000

# Supported languages
SUPPORTED = {
    'ar': 'العربية', 'en': 'English', 'tr': 'Türkçe', 'ja': '日本語',
    'fr': 'français', 'ko': '한국어', 'it': 'italiano', 'es': 'español',
    'de': 'Deutsch', 'zh-CN': '中文', 'ru': 'русский', 'pt': 'português',
    'nl': 'Nederlands', 'pl': 'polski', 'hi': 'हिन्दी'
}

LANGUAGE_NAMES = {
    'ar': 'العربية', 'en': 'English', 'tr': 'Türkçe', 'ja': '日本語',
    'fr': 'français', 'ko': '한국어', 'it': 'italiano', 'es': 'español',
    'de': 'Deutsch', 'zh-CN': '中文', 'ru': 'русский', 'pt': 'português'
}

# Translation messages
TRANSLATION_MESSAGES = {
    'ar': {
        'same_language_title': 'نفس اللغة',
        'same_language': 'الرسالة بالفعل باللغة العربية',
        'translation_failed_title': 'فشلت الترجمة',
        'translation_failed': 'لم أتمكن من ترجمة هذه الرسالة',
        'translation_error_title': 'خطأ في الترجمة',
        'translation_error': 'حدث خطأ أثناء الترجمة:',
        'original_message': 'الرسالة الأصلية',
        'to': 'إلى'
    },
    'en': {
        'same_language_title': 'Same Language',
        'same_language': 'The message is already in English',
        'translation_failed_title': 'Translation Failed',
        'translation_failed': 'Could not translate this message',
        'translation_error_title': 'Translation Error',
        'translation_error': 'An error occurred during translation:',
        'original_message': 'Original Message',
        'to': 'to'
    },
    'tr': {
        'same_language_title': 'Aynı Dil',
        'same_language': 'Mesaj zaten Türkçe',
        'translation_failed_title': 'Çeviri Başarısız',
        'translation_failed': 'Bu mesaj çevrilemedi',
        'translation_error_title': 'Çeviri Hatası',
        'translation_error': 'Çeviri sırasında bir hata oluştu:',
        'original_message': 'Orijinal Mesaj',
        'to': 'için'
    }
}


def get_translation_message(lang_code: str, key: str) -> str:
    """Get translation message in specified language."""
    return TRANSLATION_MESSAGES.get(lang_code, TRANSLATION_MESSAGES['en']).get(key, key)


def make_embed(title: str = None, description: str = None, color: discord.Color = discord.Color.blue()) -> discord.Embed:
    """Create a styled embed."""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )
    return embed


class TranslationLanguageView(discord.ui.View):
    """View for selecting translation language when user has multiple role languages."""
    
    def __init__(self, user_languages: list, message_content: str, source_lang: str):
        super().__init__(timeout=180)
        self.user_languages = user_languages  # [(lang_code, lang_name), ...]
        self.message_content = message_content
        self.source_lang = source_lang
        
        # Add buttons for each language (max 5 per row)
        for lang_code, lang_name in user_languages[:5]:  # Discord limit: 5 buttons per row
            flag_emoji = {
                'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
            }.get(lang_code, '🌐')
            
            button = discord.ui.Button(
                label=f"{flag_emoji} {lang_name}",
                style=discord.ButtonStyle.primary,
                custom_id=f"translate_{lang_code}"
            )
            button.callback = self.create_callback(lang_code, lang_name)
            self.add_item(button)
    
    def create_callback(self, target_lang: str, lang_name: str):
        """Create callback function for translation button."""
        async def callback(interaction: discord.Interaction):
            try:
                # Check if same language
                if self.source_lang == target_lang:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'same_language_title'),
                        description=get_translation_message(target_lang, 'same_language').replace('العربية', lang_name).replace('English', lang_name).replace('Türkçe', lang_name).replace('日本語', lang_name).replace('français', lang_name).replace('한국어', lang_name).replace('italiano', lang_name).replace('中文', lang_name),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Translate using cache or API
                cache_key = (hash(self.message_content), self.source_lang, target_lang)
                
                if cache_key in translation_cache:
                    translated = translation_cache[cache_key]
                else:
                    translated = GoogleTranslator(source=self.source_lang, target=target_lang).translate(self.message_content)
                    if translated:
                        translation_cache[cache_key] = translated
                        
                        # Smart cache cleaning
                        if len(translation_cache) > CACHE_MAX_SIZE:
                            excess_count = len(translation_cache) - CACHE_MAX_SIZE
                            for _ in range(excess_count):
                                if translation_cache:
                                    translation_cache.pop(next(iter(translation_cache)))
                
                if not translated:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'translation_failed_title'),
                        description=get_translation_message(target_lang, 'translation_failed'),
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Create translation embed
                source_name = LANGUAGE_NAMES.get(self.source_lang, f'Unknown ({self.source_lang})')
                flag_emoji = {
                    'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                    'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                }.get(target_lang, '🌐')
                
                emb = make_embed(
                    title=f'{flag_emoji} {lang_name}',
                    description=f'━━━━━━━━━━━━━━━━━━━━━\n{translated}\n━━━━━━━━━━━━━━━━━━━━━',
                    color=discord.Color.blue()
                )
                emb.add_field(
                    name=get_translation_message(target_lang, 'original_message'),
                    value=self.message_content[:1024] if len(self.message_content) <= 1024 else self.message_content[:1021] + '...',
                    inline=False
                )
                emb.set_footer(text=f'{source_name} → {lang_name}')
                
                await interaction.response.send_message(embed=emb, ephemeral=True)
                logger.info(f"User {interaction.user} translated message from {self.source_lang} to {target_lang}")
                
            except Exception as e:
                logger.error(f"Error in translation button callback: {e}")
                emb = make_embed(
                    title=get_translation_message(target_lang, 'translation_error_title'),
                    description=f'{get_translation_message(target_lang, "translation_error")} {str(e)}',
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
        
        return callback


class TranslateCog(commands.Cog):
    """Translation system cog"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = get_db()
        
        # Load role languages from database
        self.role_languages = {}
        self._load_role_languages()
        
        # Register context menu
        self.ctx_menu = app_commands.ContextMenu(
            name='Translate Message',
            callback=self.translate_message_context,
        )
        self.bot.tree.add_command(self.ctx_menu)
    
    def _load_role_languages(self):
        """Load role languages from database."""
        try:
            # This would load from your database
            # For now, it's a placeholder
            pass
        except Exception as e:
            logger.error(f"Error loading role languages: {e}")
    
    async def translate_message_context(self, interaction: discord.Interaction, message: discord.Message):
        """Context menu command to translate a message based on user's role languages."""
        try:
            # Get message content
            content = message.content.strip()
            
            if not content:
                emb = make_embed(
                    title='No Text Content',
                    description='⚠️ This message has no text content to translate.',
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            # Get user's role languages from database
            guild_id = str(interaction.guild.id)
            user_role_ids = [str(role.id) for role in interaction.user.roles]
            
            user_languages = []
            # TODO: Load from database
            # role_languages = await self.db.role_languages.find_one({"guild_id": guild_id})
            # if role_languages:
            #     for role_id in user_role_ids:
            #         if role_id in role_languages.get('roles', {}):
            #             lang_code = role_languages['roles'][role_id]
            #             lang_name = SUPPORTED.get(lang_code, lang_code)
            #             user_languages.append((lang_code, lang_name))
            
            # If user has no role languages, show error
            if not user_languages:
                emb = make_embed(
                    title='No Language Roles',
                    description='⚠️ You don\'t have any language roles assigned.\n\n💡 **Ask an admin to:**\n1. Use `/role setlang` to assign languages to roles\n2. Give you a role with a language assigned',
                    color=discord.Color.orange()
                )
                await interaction.response.send_message(embed=emb, ephemeral=True)
                return
            
            # Detect message language
            try:
                detected = detect(content)
            except Exception as e:
                logger.debug(f"Language detection failed: {e}")
                detected = 'auto'
            
            # If only one language, translate directly
            if len(user_languages) == 1:
                target_lang, lang_name = user_languages[0]
                
                # Check if same language
                if detected == target_lang:
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'same_language_title'),
                        description=get_translation_message(target_lang, 'same_language').replace('العربية', lang_name).replace('English', lang_name).replace('Türkçe', lang_name).replace('日本語', lang_name).replace('français', lang_name).replace('한국어', lang_name).replace('italiano', lang_name).replace('中文', lang_name),
                        color=discord.Color.orange()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    return
                
                # Translate
                try:
                    cache_key = (hash(content), detected, target_lang)
                    
                    if cache_key in translation_cache:
                        translated = translation_cache[cache_key]
                    else:
                        translated = GoogleTranslator(source=detected, target=target_lang).translate(content)
                        if translated:
                            translation_cache[cache_key] = translated
                            
                            # Smart cache cleaning
                            if len(translation_cache) > CACHE_MAX_SIZE:
                                excess_count = len(translation_cache) - CACHE_MAX_SIZE
                                for _ in range(excess_count):
                                    if translation_cache:
                                        translation_cache.pop(next(iter(translation_cache)))
                    
                    if not translated:
                        emb = make_embed(
                            title=get_translation_message(target_lang, 'translation_failed_title'),
                            description=get_translation_message(target_lang, 'translation_failed'),
                            color=discord.Color.red()
                        )
                        await interaction.response.send_message(embed=emb, ephemeral=True)
                        return
                    
                    # Create translation embed
                    source_name = LANGUAGE_NAMES.get(detected, f'Unknown ({detected})')
                    flag_emoji = {
                        'ar': '🇸🇦', 'en': '🇬🇧', 'tr': '🇹🇷',
                        'ja': '🇯🇵', 'fr': '🇫🇷', 'ko': '🇰🇷', 'it': '🇮🇹', 'zh-CN': '🇨🇳'
                    }.get(target_lang, '🌐')
                    
                    to_word = get_translation_message(target_lang, 'to')
                    emb = make_embed(
                        title=f'{flag_emoji} {lang_name}',
                        description=f'━━━━━━━━━━━━━━━━━━━━━\n{translated}\n━━━━━━━━━━━━━━━━━━━━━',
                        color=discord.Color.blue()
                    )
                    emb.add_field(
                        name=get_translation_message(target_lang, 'original_message'),
                        value=content[:1024] if len(content) <= 1024 else content[:1021] + '...',
                        inline=False
                    )
                    emb.set_footer(text=f'{source_name} → {lang_name}')
                    
                    await interaction.response.send_message(embed=emb, ephemeral=True)
                    logger.info(f"User {interaction.user} translated message from {detected} to {target_lang}")
                    
                except Exception as e:
                    logger.error(f"Translation error: {e}")
                    emb = make_embed(
                        title=get_translation_message(target_lang, 'translation_error_title'),
                        description=f'{get_translation_message(target_lang, "translation_error")} {str(e)}',
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=emb, ephemeral=True)
            
            else:
                # Multiple languages - show selection buttons
                view = TranslationLanguageView(user_languages, content, detected)
                
                emb = make_embed(
                    title='🌐 Choose Translation Language',
                    description='You have multiple language roles. Please select your preferred language:',
                    color=discord.Color.blurple()
                )
                emb.add_field(
                    name='📝 Original Message',
                    value=content[:1024] if len(content) <= 1024 else content[:1021] + '...',
                    inline=False
                )
                
                await interaction.response.send_message(embed=emb, view=view, ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error in translate_message_context: {e}")
            emb = make_embed(
                title='Error',
                description=f'❌ An error occurred: {str(e)}',
                color=discord.Color.red()
            )
            try:
                await interaction.response.send_message(embed=emb, ephemeral=True)
            except:
                await interaction.followup.send(embed=emb, ephemeral=True)
    
    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)


async def setup(bot):
    await bot.add_cog(TranslateCog(bot))
