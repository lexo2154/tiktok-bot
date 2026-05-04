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
app = Flask(__name__)

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
        'welcome': (
            "👋 <b>Welcome to the TikTok Analytics & Download Bot!</b>\n\n"
            "Send me any TikTok video link, and I will instantly analyze the statistics and video quality, "
            "providing high-quality video or audio download options.\n\n"
            "🚀 <i>Send the link now to get started!</i>\n"
            "⚙️ <i>Use /language to change the bot language.</i>"
        ),
        'analyzing': "⏳ Analyzing data...",
        'invalid': "⚠️ Invalid link or the video has been deleted.",
        'error': "❌ An error occurred while processing the data.",
        'lang_changed': "✅ Language successfully changed to English.",
        'lang_menu': "🌐 Choose your preferred language:",
        'download_video': "📥 Downloading video (HD)...",
        'download_audio': "🎵 Downloading audio file (MP3)...",
        'sending': "⏳ Sending file...",
        'error_download': "❌ An error occurred while trying to send the file.",
        'btn_video': "🎥 Download Video (HD)",
        'btn_audio': "🎵 Download Audio (MP3)",
        'author': "Author",
        'published': "Published",
        'statistics': "Statistics",
        'information': "Information",
        'quality': "Quality",
        'tags': "Tags",
        'source': "Source",
        'region': "Region",
        'shadow_ban': "Shadow ban",
    },
    'ar': {
        'welcome': (
            "👋 <b>مرحباً بك في بوت تحليل وتحميل فيديوهات تيك توك!</b>\n\n"
            "أرسل لي أي رابط فيديو من تيك توك، وسأقوم بتحليل الإحصائيات وجودة الفيديو فوراً، "
            "مع توفير خيارات لتحميل الفيديو أو الصوت بجودة عالية.\n\n"
            "🚀 <i>أرسل الرابط الآن لنبدأ!</i>\n"
            "⚙️ <i>استخدم /language لتغيير لغة البوت.</i>"
        ),
        'analyzing': "⏳ جارٍ تحليل البيانات...",
        'invalid': "⚠️ رابط غير صالح أو تم حذف الفيديو.",
        'error': "❌ حدث خطأ أثناء معالجة البيانات.",
        'lang_changed': "✅ تم تغيير اللغة إلى العربية بنجاح.",
        'lang_menu': "🌐 اختر لغتك المفضلة:",
        'download_video': "📥 جاري تحميل الفيديو (HD)...",
        'download_audio': "🎵 جاري تحميل الصوت (MP3)...",
        'sending': "⏳ جاري إرسال الملف...",
        'error_download': "❌ حدث خطأ أثناء محاولة إرسال الملف.",
        'btn_video': "🎥 تحميل الفيديو (HD)",
        'btn_audio': "🎵 تحميل الصوت (MP3)",
        'author': "الناشر",
        'published': "تاريخ النشر",
        'statistics': "الإحصائيات",
        'information': "المعلومات",
        'quality': "الجودة",
        'tags': "الوسوم",
        'source': "المصدر",
        'region': "المنطقة",
        'shadow_ban': "حظر الظل",
    },
    'ru': {
        'welcome': (
            "👋 <b>Добро пожаловать в бот для анализа и скачивания видео из TikTok!</b>\n\n"
            "Отправьте мне любую ссылку на видео из TikTok, и я мгновенно проанализирую статистику и качество видео, "
            "предоставив варианты скачивания видео или аудио в высоком качестве.\n\n"
            "🚀 <i>Отправьте ссылку сейчас, чтобы начать!</i>\n"
            "⚙️ <i>Используйте /language чтобы изменить язык.</i>"
        ),
        'analyzing': "⏳ Идет анализ данных...",
        'invalid': "⚠️ Неверная ссылка или видео было удалено.",
        'error': "❌ Произошла ошибка при обработке данных.",
        'lang_changed': "✅ Язык успешно изменен на русский.",
        'lang_menu': "🌐 Выберите предпочитаемый язык:",
        'download_video': "📥 Скачиваю видео (HD)...",
        'download_audio': "🎵 Скачиваю аудио (MP3)...",
        'sending': "⏳ Отправляю файл...",
        'error_download': "❌ Произошла ошибка при попытке отправить файл.",
        'btn_video': "🎥 Скачать видео (HD)",
        'btn_audio': "🎵 Скачать аудио (MP3)",
        'author': "Автор",
        'published': "Опубликовано",
        'statistics': "Статистика",
        'information': "Информация",
        'quality': "Качество",
        'tags': "Теги",
        'source': "Источник",
        'region': "Регион",
        'shadow_ban': "Теневой бан",
    }
}

def t(chat_id, key):
    lang = user_languages.get(chat_id, 'en') # الافتراضي هو الإنجليزية
    return LANGUAGES[lang].get(key, LANGUAGES['en'][key])

def get_country_full_name(code):
    return COUNTRY_NAMES.get(code.upper(), code)

def get_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return "📍"
    return "".join(chr(ord(c.upper()) + 127397) for c in country_code)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    bot.reply_to(message, t(chat_id, 'welcome'), parse_mode="HTML")

@bot.message_handler(commands=['language', 'lang'])
def send_language_menu(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
        InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        InlineKeyboardButton("🇸🇦 العربية", callback_data="lang_ar")
    )
    bot.send_message(chat_id, t(chat_id, 'lang_menu'), reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def handle_language_change(call):
    chat_id = call.message.chat.id
    lang = call.data.split('_')[1] # استخراج كود اللغة
    user_languages[chat_id] = lang
    
    bot.answer_callback_query(call.id, t(chat_id, 'lang_changed'))
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=call.message.message_id,
        text=f"{t(chat_id, 'lang_menu')}\n\n{t(chat_id, 'lang_changed')}",
        reply_markup=None
    )

@bot.message_handler(func=lambda message: True)
def handle_tiktok(message):
    chat_id = message.chat.id
    user_text = message.text
    if 'tiktok.com' in user_text:
        wait_msg = bot.reply_to(message, t(chat_id, 'analyzing'))
        
        try:
            api_url = f"https://www.tikwm.com/api/?url={user_text}"
            res = requests.get(api_url, timeout=15).json()
            
            if res.get('code') == 0:
                data = res['data']
                video_id = data.get('id')
                
                # استخراج بيانات الحظر
                is_private = data.get('private_item', False)
                is_ad = data.get('is_ad', False)
                if is_private or is_ad:
                    shadow_status = "Yes ⚠️"
                elif data.get('play_count', 0) < 10 and data.get('digg_count', 0) == 0:
                    shadow_status = "Maybe 🧐"
                else:
                    shadow_status = "No ✅"
                
                author_name = data.get('author', {}).get('nickname', 'Unknown Author')
                author_unique_id = data.get('author', {}).get('unique_id', 'unknown')
                
                create_time = data.get('create_time', 0)
                if create_time:
                    publish_date = datetime.datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    publish_date = "Unknown"
                
                title = data.get('title', 'No Title Provided')
                region_code = data.get('region', 'UN')
                country_name = get_country_full_name(region_code)
                flag = get_flag_emoji(region_code)
                
                local_time = datetime.datetime.now() + datetime.timedelta(hours=1)
                now = local_time.strftime('%Y, %H:%M:%S')
                
                res_w = data.get('width', 1080)
                res_h = data.get('height', 1920)
                
                size_bytes = data.get('size', 0) or 0
                size_mb = size_bytes / (1024 * 1024)
                duration = data.get('duration', 1) or 1
                bitrate = size_mb / duration if duration > 0 else 0
                
                if bitrate > 0.3:
                    fps = 60
                else:
                    fps = 30
                    
                quality_res = f"{res_h}p{fps}"

                hashtags = [word for word in title.split() if word.startswith('#')]
                if hashtags:
                    tags_text = " ".join(hashtags)
                else:
                    tags_text = "#TikTok"

                music_info = data.get('music_info', {})
                music_title = music_info.get('title', 'Original Sound')
                music_author = music_info.get('author', 'Unknown Artist')
                
                encoded_query = urllib.parse.quote(f"{music_title} {music_author}")
                youtube_link = f"https://www.youtube.com/results?search_query={encoded_query}"
                spotify_link = f"https://open.spotify.com/search/{encoded_query}"

                stats_message = (
                    f"🎬 <b>VIDEO • ANALYTICS</b>\n"
                    f"• {now}\n\n"
                    f"💬 <code>{title[:60]}...</code>\n"
                    f'👤 {t(chat_id, "author")}: <a href="https://www.tiktok.com/@{author_unique_id}">{author_name} (@{author_unique_id})</a>\n'
                    f"📅 {t(chat_id, 'published')}: <b>{publish_date}</b>\n"
                    f'🎵 <b>{music_title} - {music_author}</b> • {duration}s\n'
                    f'   <a href="{youtube_link}">▶️ YouTube</a> | <a href="{spotify_link}">🟢 Spotify</a>\n\n'
                    f"📊 <b>{t(chat_id, 'statistics')}</b>\n"
                    f"• 👁️ {data.get('play_count', 0)} Views\n"
                    f"• ❤️ {data.get('digg_count', 0)} Likes\n"
                    f"• 💬 {data.get('comment_count', 0)} Comments\n"
                    f"• 🔖 {data.get('collect_count', 0)} Favorites\n"
                    f"• 🔗 {data.get('share_count', 0)} Shares\n"
                    f"• 📥 {data.get('download_count', 0)} Downloads\n\n"
                    f"ℹ️ <b>{t(chat_id, 'information')}</b>\n"
                    f"• 🆔 ID | <code>{data.get('id')}</code>\n"
                    f"• 📥 {t(chat_id, 'source')} | Browser\n"
                    f"• {flag} {t(chat_id, 'region')} | {country_name}\n"
                    f"• 👻 {t(chat_id, 'shadow_ban')} | <b>{shadow_status}</b>\n\n"
                    f"⭐ <b>{t(chat_id, 'quality')}</b>\n"
                    f"• 🌐 Browser | {res_w}x{res_h}\n"
                    f"• 📱 Phone | {res_w}x{res_h}\n"
                    f"<blockquote>🌐 📱 play_addr 🌐 📱\n"
                    f"original_{res_w}_{res_h}\n"
                    f"{quality_res} • {bitrate:.1f} MBps •\n"
                    f"h264 • {size_mb:.1f} MB\n\n"
                    f"Original | {res_w}x{res_h}\n"
                    f"VQ Score | 0</blockquote>\n\n"
                    f"📝 <b>{t(chat_id, 'tags')}</b>\n"
                    f"<blockquote>{tags_text}</blockquote>\n\n"
                    f'⚡ <b>Created by <a href="https://t.me/lexo_20">𝐋𝐞_𝐱𝐨</a></b>'
                )
                
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton(t(chat_id, 'btn_video'), callback_data=f"vid_{video_id}"),
                    InlineKeyboardButton(t(chat_id, 'btn_audio'), callback_data=f"mp3_{video_id}")
                )
                
                bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=wait_msg.message_id,
                    text=stats_message,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            else:
                bot.edit_message_text(t(chat_id, 'invalid'), chat_id, wait_msg.message_id)
        
        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text(t(chat_id, 'error'), chat_id, wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('vid_') or call.data.startswith('mp3_'))
def handle_download(call):
    chat_id = call.message.chat.id
    action, video_id = call.data.split('_')
    
    bot.answer_callback_query(call.id, t(chat_id, 'sending'))
    
    try:
        api_url = f"https://www.tikwm.com/api/?url=https://www.tiktok.com/@any/video/{video_id}"
        res = requests.get(api_url, timeout=15).json()
        
        if res.get('code') == 0:
            data = res['data']
            
            if action == 'vid':
                bot.send_message(chat_id, t(chat_id, 'download_video'))
                video_url = data.get('hdplay') or data.get('play')
                bot.send_video(chat_id, video_url)
                
            elif action == 'mp3':
                bot.send_message(chat_id, t(chat_id, 'download_audio'))
                audio_url = data.get('music')
                bot.send_audio(chat_id, audio_url)
                
    except Exception as e:
        bot.send_message(chat_id, t(chat_id, 'error_download'))

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t_thread = threading.Thread(target=run_bot)
    t_thread.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
