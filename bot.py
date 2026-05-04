import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import os
import threading
from flask import Flask
import urllib.parse

# جلب التوكن من متغيرات البيئة Environment Variables
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Error: BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TOKEN.strip())

# قاموس لتخزين لغة كل مستخدم (افتراضياً الإنجليزية)
user_languages = {}

# إعداد خادم ويب مجاني لإبقاء السيرفر نشطاً على Render
app = Flask(name)  # ✅ FIXED HERE

@app.route('/')
def home():
    return "Bot is running and active!"

COUNTRY_NAMES = {
    'DZ': 'Algeria', 'SA': 'Saudi Arabia', 'EG': 'Egypt', 'MA': 'Morocco',
    'IQ': 'Iraq', 'JP': 'Japan', 'US': 'United States', 'ID': 'Indonesia',
    'TR': 'Turkey', 'AE': 'United Arab Emirates', 'KW': 'Kuwait', 'QA': 'Qatar',
    'JO': 'Jordan', 'LY': 'Libya', 'TN': 'Tunisia', 'OM': 'Oman', 'FR': 'France',
    'SY': 'Syria', 'LB': 'Lebanon', 'PS': 'Palestine', 'YE': 'Yemen'
}

# النصوص المخصصة لكل لغة
LANGUAGES = {
    'en': {
        'welcome': "👋 Welcome",
        'analyzing': "⏳ Analyzing...",
        'invalid': "⚠️ Invalid link",
        'error': "❌ Error",
        'lang_changed': "✅ Language changed",
        'lang_menu': "🌐 Choose language:",
        'download_video': "📥 Downloading video...",
        'download_audio': "🎵 Downloading audio...",
        'sending': "⏳ Sending...",
        'error_download': "❌ Download error",
        'btn_video': "🎥 Video",
        'btn_audio': "🎵 Audio",
        'author': "Author",
        'published': "Published",
        'statistics': "Statistics",
        'information': "Info",
        'quality': "Quality",
        'tags': "Tags",
        'source': "Source",
        'region': "Region",
        'shadow_ban': "Shadow ban",
    },
    'ar': {
        'welcome': "👋 مرحبا",
        'analyzing': "⏳ جاري التحليل...",
        'invalid': "⚠️ رابط غير صالح",
        'error': "❌ خطأ",
        'lang_changed': "✅ تم تغيير اللغة",
        'lang_menu': "🌐 اختر اللغة:",
        'download_video': "📥 جاري تحميل الفيديو...",
        'download_audio': "🎵 جاري تحميل الصوت...",
        'sending': "⏳ إرسال...",
        'error_download': "❌ خطأ في التحميل",
        'btn_video': "🎥 فيديو",
        'btn_audio': "🎵 صوت",
        'author': "الناشر",
        'published': "تاريخ النشر",
        'statistics': "الإحصائيات",
        'information': "معلومات",
        'quality': "الجودة",
        'tags': "الوسوم",
        'source': "المصدر",
        'region': "المنطقة",
        'shadow_ban': "حظر الظل",
    }
}

def t(chat_id, key):
    lang = user_languages.get(chat_id, 'en')
    return LANGUAGES[lang].get(key, LANGUAGES['en'][key])

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, t(message.chat.id, 'welcome'))

@bot.message_handler(func=lambda m: True)
def handle(message):
    chat_id = message.chat.id
    text = message.text

    if "tiktok.com" not in text:
        return

    wait = bot.reply_to(message, t(chat_id, 'analyzing'))

    try:
        api_url = f"https://www.tikwm.com/api/?url={text}"
        res = requests.get(api_url, timeout=15).json()

        if res.get("code") != 0:
            return bot.edit_message_text(
                t(chat_id, 'invalid'),
                chat_id,
                wait.message_id
            )

        data = res["data"]

        music = data.get("music_info", {})
        sound_title = music.get("title", "Original Sound")
        sound_author = music.get("author", "Unknown")

        query = urllib.parse.quote(f"{sound_title} {sound_author}")
        youtube = f"https://www.youtube.com/results?search_query={query}"
        spotify = f"https://open.spotify.com/search/{query}"

        stats = (
            f"🎵 Sound: {sound_title} - {sound_author}\n"
            f"▶️ YouTube | 🟢 Spotify"
        )

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🎥 Video", callback_data=f"vid_{data['id']}"),
            InlineKeyboardButton("🎵 Audio", callback_data=f"mp3_{data['id']}")
        )

        bot.edit_message_text(
            stats,
            chat_id,
            wait.message_id,
            reply_markup=markup
        )

    except Exception as e:
        print(e)
        bot.edit_message_text(t(chat_id, 'error'), chat_id, wait.message_id)


def run_bot():
    bot.polling(none_stop=True)

if name == 'main':
    threading.Thread(target=run_bot).start()

    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
