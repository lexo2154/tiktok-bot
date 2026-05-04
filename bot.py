import os
import telebot
import requests
import threading
from flask import Flask
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =========================
# 🔐 TOKEN من Render ENV
# =========================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise Exception("BOT_TOKEN not found in environment variables")

bot = telebot.TeleBot(TOKEN)

# =========================
# 🌐 Flask (keep alive)
# =========================
app = Flask(name)

@app.route('/')
def home():
    return "Bot is running"

# =========================
# 📩 Start Command (اختياري)
# =========================
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Bot is online!")

# =========================
# 🎥 Main Handler (TikTok)
# =========================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text

    wait_msg = bot.send_message(message.chat.id, "⏳ Processing...")

    try:
        api_url = f"https://www.tikwm.com/api/?url={url}"
        res = requests.get(api_url, timeout=15).json()

        if res.get('code') == 0:
            data = res['data']

            video_id = data.get('id', 'unknown')
            country_name = data.get('region', 'Unknown')
            flag = "🌍"
            shadow_status = "No"

            res_w = data.get('width', 720)
            res_h = data.get('height', 1280)

            bitrate = data.get('bitrate', 0) / 1000
            size_mb = data.get('size', 0) / (1024 * 1024)

            quality_res = f"{res_w}x{res_h}"

            tags_text = "TikTok Video"

            stats_message = (
                f"🎵 <b>Sound</b> • {data.get('duration', 0)}s\n\n"
                f"📊 <b>Statistics</b>\n"
                f"• 👁️ {data.get('play_count', 0)} Views\n"
                f"• ❤️ {data.get('digg_count', 0)} Likes\n"
                f"• 💬 {data.get('comment_count', 0)} Comments\n"
                f"• 🔖 {data.get('collect_count', 0)} Favorites\n"
                f"• 🔗 {data.get('share_count', 0)} Shares\n"
                f"• 📥 {data.get('download_count', 0)} Downloads\n\n"
                f"ℹ️ <b>Information</b>\n"
                f"• 🆔 ID | <code>{video_id}</code>\n"
                f"• 📥 Source | Browser\n"
                f"• {flag} Region | {country_name}\n"
                f"• 👻 Shadow ban | <b>{shadow_status}</b>\n\n"
                f"⭐ <b>Quality</b>\n"
                f"• 🌐 Browser | {res_w}x{res_h}\n"
                f"• 📱 Phone | {res_w}x{res_h}\n"
                f"<blockquote>\n"
                f"original_{res_w}_{res_h}\n"
                f"{quality_res} • {bitrate:.1f} MBps •\n"
                f"h264 • {size_mb:.1f} MB\n\n"
                f"Original | {res_w}x{res_h}\n"
                f"VQ Score | 0</blockquote>\n\n"
                f"📝 <b>Tags</b>\n"
                f"<blockquote>{tags_text}</blockquote>\n\n"
                f"⚡ <b>re:TikTok Checker & Downloader</b>"
            )

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
            bot.edit_message_text(
                "⚠️ Invalid link or video deleted.",
                message.chat.id,
                wait_msg.message_id
            )

    except Exception as e:
        print(e)
        bot.edit_message_text(
            "❌ Error processing request.",
            message.chat.id,
            wait_msg.message_id
        )

# =========================
# ⬇️ Download Handler
# =========================
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
                video_url = data.get('hdplay') or data.get('play')
                bot.send_video(call.message.chat.id, video_url)

            elif action == 'mp3':
                audio_url = data.get('music')
                bot.send_audio(call.message.chat.id, audio_url)

    except Exception as e:
        bot.send_message(call.message.chat.id, "❌ Download failed.")

# =========================
# 🚀 Run Bot
# =========================
def run_bot():
    bot.polling(none_stop=True)

if name == 'main':
    t = threading.Thread(target=run_bot)
    t.start()

    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)