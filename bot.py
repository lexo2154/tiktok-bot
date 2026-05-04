import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import os
import threading
from flask import Flask
import urllib.parse

TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Error: BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TOKEN.strip())

user_languages = {}

app = Flask(name)

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

LANGUAGES = {
    'en': {
        'welcome': "👋 <b>Welcome!</b>",
        'analyzing': "⏳ Analyzing data...",
        'invalid': "⚠️ Invalid link",
        'error': "❌ Error",
        'lang_changed': "✅ Language changed",
        'lang_menu': "🌐 Choose language:",
        'download_video': "📥 Downloading video...",
        'download_audio': "🎵 Downloading audio...",
        'sending': "⏳ Sending...",
        'error_download': "❌ Download error",
        'btn_video': "🎥 Video HD",
        'btn_audio': "🎵 Audio MP3",
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
        'welcome': "👋 <b>مرحبا!</b>",
        'analyzing': "⏳ جاري التحليل...",
        'invalid': "⚠️ رابط غير صالح",
        'error': "❌ خطأ",
        'lang_changed': "✅ تم تغيير اللغة",
        'lang_menu': "🌐 اختر اللغة:",
        'download_video': "📥 جاري تحميل الفيديو...",
        'download_audio': "🎵 جاري تحميل الصوت...",
        'sending': "⏳ إرسال...",
        'error_download': "❌ خطأ في التحميل",
        'btn_video': "🎥 فيديو HD",
        'btn_audio': "🎵 صوت MP3",
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

def get_country_full_name(code):
    return COUNTRY_NAMES.get(code.upper(), code)

def get_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return "📍"
    return "".join(chr(ord(c.upper()) + 127397) for c in country_code)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, t(message.chat.id, 'welcome'), parse_mode="HTML")

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
            return bot.edit_message_text(t(chat_id,'invalid'), chat_id, wait.message_id)

        data = res["data"]

        # 🔥 SOUND FIX (IMPROVED)
        music = data.get("music_info", {}) or {}

        sound_title = music.get("title")
        sound_author = music.get("author")

        # fallback system (important)
        if not sound_title:
            sound_title = data.get("music", "Original Sound")

        if not sound_author:
            sound_author = "TikTok Audio"

        query = urllib.parse.quote(f"{sound_title} {sound_author}")

        youtube = f"https://www.youtube.com/results?search_query={query}"
        spotify = f"https://open.spotify.com/search/{query}"

        stats = (
            f"🎵 <b>Sound Info</b>\n"
            f"• {sound_title} - {sound_author}\n\n"
            f"▶️ <a href='{youtube}'>YouTube</a> | "
            f"🟢 <a href='{spotify}'>Spotify</a>"
        )

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton(t(chat_id,'btn_video'), callback_data=f"vid_{data['id']}"),
            InlineKeyboardButton(t(chat_id,'btn_audio'), callback_data=f"mp3_{data['id']}")
        )

        bot.edit_message_text(stats, chat_id, wait.message_id,
                              parse_mode="HTML", reply_markup=markup)

    except Exception as e:
        print(e)
        bot.edit_message_text(t(chat_id,'error'), chat_id, wait.message_id)


bot.polling()
