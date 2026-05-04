import time
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import datetime
import os
import threading
from flask import Flask

# جلب التوكن من متغيرات البيئة Environment Variables
TOKEN = os.environ.get('BOT_TOKEN')

if not TOKEN:
    raise ValueError("Error: BOT_TOKEN is not set in environment variables.")

bot = telebot.TeleBot(TOKEN.strip())

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

def get_country_full_name(code):
    return COUNTRY_NAMES.get(code.upper(), code)

def get_flag_emoji(country_code):
    if not country_code or len(country_code) != 2:
        return "📍"
    return "".join(chr(ord(c.upper()) + 127397) for c in country_code)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Send a TikTok link and I will provide a professional HTML-formatted analysis 🚀")

@bot.message_handler(func=lambda message: True)
def handle_tiktok(message):
    user_text = message.text
    if 'tiktok.com' in user_text:
        wait_msg = bot.reply_to(message, "⏳ Analyzing...")
        
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
                
                # استخراج المعلومات الأساسية
                author_name = data.get('author', {}).get('nickname', 'Unknown Author')
                author_unique_id = data.get('author', {}).get('unique_id', 'unknown')
                
                # استخراج وقت النشر بالضبط
                create_time = data.get('create_time', 0)
                if create_time:
                    publish_date = datetime.datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
                else:
                    publish_date = "Unknown"
                
                title = data.get('title', 'No Title Provided')
                region_code = data.get('region', 'UN')
                country_name = get_country_full_name(region_code)
                flag = get_flag_emoji(region_code)
                now = datetime.datetime.now().strftime('%Y, %H:%M:%S')
                
                # استخراج الأبعاد (Width و Height) مباشرة من استجابة API
                res_w = data.get('width', 1080)
                res_h = data.get('height', 1920)
                
                # استخراج الحجم والمدة وحساب معدل نقل البيانات (Bitrate)
                size_bytes = data.get('size', 0) or 0
                size_mb = size_bytes / (1024 * 1024)
                duration = data.get('duration', 1) or 1
                bitrate = size_mb / duration if duration > 0 else 0
                
                # حساب معدل إطارات الفيديو (FPS) ديناميكياً
                if bitrate > 0.3:
                    fps = 60
                else:
                    fps = 30
                    
                quality_res = f"{res_h}p{fps}" # تنسيق الجودة ليتناسب مع الأبعاد

                # استخراج جميع الهاشتاجات من العنوان
                hashtags = [word for word in title.split() if word.startswith('#')]
                if hashtags:
                    tags_text = " ".join(hashtags)
                else:
                    tags_text = "#TikTok"

                # بناء الرسالة باللغة الإنجليزية
                stats_message = (
                    f"🎬 <b>VIDEO • ANALYTICS</b>\n"
                    f"• {now}\n\n"
                    f"💬 <code>{title[:60]}...</code>\n"
                    f"👤 Author: <b>{author_name} (@{author_unique_id})</b>\n"
                    f"📅 Published: <b>{publish_date}</b>\n"
                    f"🎵 <b>Sound</b> • {data.get('duration', 0)}s\n\n"
                    f"📊 <b>Statistics</b>\n"
                    f"• 👁️ {data.get('play_count', 0)} Views\n"
                    f"• ❤️ {data.get('digg_count', 0)} Likes\n"
                    f"• 💬 {data.get('comment_count', 0)} Comments\n"
                    f"• 🔖 {data.get('collect_count', 0)} Favorites\n"
                    f"• 🔗 {data.get('share_count', 0)} Shares\n"
                    f"• 📥 {data.get('download_count', 0)} Downloads\n\n"
                    f"ℹ️ <b>Information</b>\n"
                    f"• 🆔 ID | <code>{data.get('id')}</code>\n"
                    f"• 📥 Source | Browser\n"
                    f"• {flag} Region | {country_name}\n"
                    f"• 👻 Shadow ban | <b>{shadow_status}</b>\n\n"
                    f"⭐ <b>Quality</b>\n"
                    f"• 🌐 Browser | {res_w}x{res_h}\n"
                    f"• 📱 Phone | {res_w}x{res_h}\n"
                    f"<blockquote>🌐 📱 play_addr 🌐 📱\n"
                    f"original_{res_w}_{res_h}\n"
                    f"{quality_res} • {bitrate:.1f} MBps •\n"
                    f"h264 • {size_mb:.1f} MB\n\n"
                    f"Original | {res_w}x{res_h}\n"
                    f"VQ Score | 0</blockquote>\n\n"
                    f"📝 <b>Tags</b>\n"
                    f"<blockquote>{tags_text}</blockquote>\n\n"
                    f"⚡ <b>re:TikTok Checker & Downloader</b>"
                )
                
                # إضافة أزرار التحميل
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("🎥 Download Video (HD)", callback_data=f"vid_{video_id}"),
                    InlineKeyboardButton("🎵 Download Audio (MP3)", callback_data=f"mp3_{video_id}")
                )
                
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=wait_msg.message_id,
                    text=stats_message,
                    parse_mode="HTML",
                    reply_markup=markup
                )
            else:
                bot.edit_message_text("⚠️ Invalid link or the video has been deleted.", message.chat.id, wait_msg.message_id)
        
        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text("❌ An error occurred while processing the data.", message.chat.id, wait_msg.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('vid_') or call.data.startswith('mp3_'))
def handle_download(call):
    action, video_id = call.data.split('_')
    
    bot.answer_callback_query(call.id, "⏳ Sending file...")
    
    try:
        api_url = f"https://www.tikwm.com/api/?url=https://www.tiktok.com/@any/video/{video_id}"
        res = requests.get(api_url, timeout=15).json()
        
        if res.get('code') == 0:
            data = res['data']
            
            if action == 'vid':
                bot.send_message(call.message.chat.id, "📥 Downloading video (HD)...")
                video_url = data.get('hdplay') or data.get('play')
                bot.send_video(call.message.chat.id, video_url)
                
            elif action == 'mp3':
                bot.send_message(call.message.chat.id, "🎵 Downloading audio file (MP3)...")
                audio_url = data.get('music')
                bot.send_audio(call.message.chat.id, audio_url)
                
    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ An error occurred while trying to send the file.")

def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    t = threading.Thread(target=run_bot)
    t.start()
    
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
