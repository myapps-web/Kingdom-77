# Kingdom-77 Discord Bot

مستودع بسيط لبوت ديسكورد مخصّص للترجمة.

ملفات مهمة:
- `discord-bot/Main.py`: نقطة تشغيل البوت.
- `discord-bot/requirements.txt`: تبعيات البوت.
- `cogs/cogs/*.py`: ملفات Cogs (الأوامر والوظائف).

تشغيل محلي (Windows / PowerShell):

1. أنشئ ملف `.env` داخل المجلد `discord-bot/` أو في جذر المشروع مع المتغير:
```
TOKEN=YOUR_DISCORD_BOT_TOKEN
```

2. فعّل البيئة الافتراضية ثم ثبّت التبعيات:
```powershell
# تفعيل البيئة الافتراضية (إن وُجدت)
& ".venv/Scripts/Activate.ps1"
pip install -r discord-bot/requirements.txt
```

3. شغّل البوت:
```powershell
cd discord-bot
python Main.py
```

نشر على Replit:
- ارفع المجلد أو اربط المستودع بـ Replit.
- في Settings -> Secrets أدخل `TOKEN` بقيمة توكن البوت.
- تأكد أن `requirements.txt` موجود في مشروع Replit (الملف `discord-bot/requirements.txt` موجود في هذا الريبو).
- اضبط أمر التشغيل إلى: `python Main.py` داخل مجلد `discord-bot` أو اجعل ملف `Main.py` هو ملف التشغيل.

ملاحظات أمان:
- لا ترفع توكن البوت إلى المستودع العام. استخدم متغيرات البيئة/Secrets على Replit.
- `.env.example` موجود هنا كمثال فقط.
