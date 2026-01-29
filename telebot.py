import requests
import time
import g4f

TOKEN = "GEDBI0TFNRTWSMYCKCUXCSQYHDDUUOGRZRRPZKSNMCNDEUBQBDZXHWIFQZJAVBIA"
BASE_URL = f"https://botapi.rubika.ir/v3/{TOKEN}"
AI_STATE = {}

def set_bot_commands():
    commands = {
        "bot_commands": [
            {"command": "start", "description": "شروع مجدد"},
            {"command": "help", "description": "راهنما"},
            {"command": "ai", "description": "پاسخ متنی هوش مصنوعی"},
            {"command": "img", "description": "ساخت تصویر با هوش مصنوعی"},
            {"command": "video", "description": "ساخت ویدیو با هوش مصنوعی"}
        ]
    }
    url = f"{BASE_URL}/setCommands"
    response = requests.post(url, json=commands)
    print("📌 ثبت دستورات ربات:", response.text)

def api_call(method, payload=None):
    try:
        url = f"{BASE_URL}/{method}"
        res = requests.post(url, json=payload or {})
        return res.json().get("data", {}) if res.status_code == 200 else {}
    except Exception as e:
        print("[API Exception]", e)
        return {}

def send_message(chat_id, text, reply_to=None, inline_keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_to:
        payload["reply_to_message_id"] = reply_to
    
    # اضافه کردن کیبورد اینلاین
    if inline_keyboard:
        payload["inline_keyboard"] = inline_keyboard
    
    return api_call("sendMessage", payload)

def get_updates(offset=None):
    payload = {}
    if offset:
        payload["offset_id"] = offset
    return api_call("getUpdates", payload)

def handle_callback_query(callback):
    """مدیریت کلیک روی دکمه‌های اینلاین"""
    try:
        chat_id = callback.get("chat_id")
        data = callback.get("data")
        message_id = callback.get("message_id")
        user_id = callback.get("user_id")
        
        print(f"[CALLBACK] chat_id={chat_id} data={data} user_id={user_id}")
        
        if data == "help":
            send_message(chat_id, "📋 لیست دستورات:\n/start\n/help\n/ai\n/img\n/video\n/panel", reply_to=message_id)
        
        elif data == "ai_chat":
            AI_STATE[chat_id] = "ai_text"
            send_message(chat_id, "🧠 لطفاً سوالت رو بفرست:", reply_to=message_id)
        
        elif data == "ai_image":
            AI_STATE[chat_id] = "ai_image"
            send_message(chat_id, "🖼️ موضوع تصویر چیست؟", reply_to=message_id)
        
        elif data == "ai_video":
            AI_STATE[chat_id] = "ai_video"
            send_message(chat_id, "🎬 موضوع ویدیو چیست؟", reply_to=message_id)
        
        elif data == "panel":
            send_message(chat_id, "📊 پنل شما فعال است.\n\nآمار شما:\n- تعداد پیام‌ها: 0\n- اعتبار باقی‌مانده: نامحدود", reply_to=message_id)
        
        elif data == "close":
            # می‌توانید پیام را حذف یا ویرایش کنید
            send_message(chat_id, "❌ کیبورد بسته شد.", reply_to=message_id)
        
    except Exception as e:
        print("[handle_callback error]", e)

def handle_message(msg):
    try:
        if msg.get("type") != "NewMessage":
            return

        chat_id = msg["chat_id"]
        new_msg = msg["new_message"]
        text = new_msg.get("text", "").strip()
        msg_id = new_msg.get("message_id")

        if not text:
            return

        print(f"[NEW MSG] chat_id={chat_id} message_id={msg_id} text={text}")

        if text == "/start":
            # ایجاد کیبورد اینلاین
            keyboard = [
                [
                    {"text": "🧠 چت هوش مصنوعی", "data": "ai_chat"},
                    {"text": "🖼️ ساخت تصویر", "data": "ai_image"}
                ],
                [
                    {"text": "🎬 ساخت ویدیو", "data": "ai_video"},
                    {"text": "📊 پنل کاربری", "data": "panel"}
                ],
                [
                    {"text": "📋 راهنما", "data": "help"},
                    {"text": "❌ بستن", "data": "close"}
                ]
            ]
            
            welcome_text = """🚀 سلام! به ربات هوش مصنوعی خوش آمدید!

🔸 می‌توانید از دکمه‌های زیر استفاده کنید یا دستورات را تایپ نمایید.

💡 دستورات متنی:
• `/ai متن` - چت با هوش مصنوعی
• `/img متن` - ساخت تصویر
• `/video متن` - ساخت ویدیو
• `/panel` - پنل کاربری

کانال ما: @rubika_bots"""

            send_message(chat_id, welcome_text, reply_to=msg_id, inline_keyboard=keyboard)
            return

        if text == "/help":
            keyboard = [
                [
                    {"text": "🧠 شروع چت AI", "data": "ai_chat"},
                    {"text": "📊 پنل کاربری", "data": "panel"}
                ]
            ]
            send_message(chat_id, "📋 راهنمای ربات:\n\nاز دکمه‌های زیر استفاده کنید یا دستورات را تایپ نمایید.", 
                        reply_to=msg_id, inline_keyboard=keyboard)
            return

        if chat_id in AI_STATE:
            mode = AI_STATE.pop(chat_id)
            if mode == "ai_text":
                send_message(chat_id, "⏳ در حال پردازش...", reply_to=msg_id)
                reply = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4,
                    messages=[{"role": "user", "content": text}]
                )
                send_message(chat_id, reply, reply_to=msg_id)
            elif mode == "ai_image":
                url = f"https://image.pollinations.ai/prompt/{text.replace(' ', '%20')}"
                send_message(chat_id, f"🖼️ تصویر ساخته شد:\n{url}", reply_to=msg_id)
            elif mode == "ai_video":
                url = f"https://api.memegen.link/images/custom/{text.replace(' ', '_')}.gif?background=https://i.imgur.com/8pQe9Qp.jpeg"
                send_message(chat_id, f"🎬 ویدیو ساخته شد:\n{url}", reply_to=msg_id)
            return

        if text.startswith("/ai"):
            arg = text[3:].strip()
            if arg:
                send_message(chat_id, "⏳ در حال پردازش...", reply_to=msg_id)
                reply = g4f.ChatCompletion.create(
                    model=g4f.models.gpt_4,
                    messages=[{"role": "user", "content": arg}]
                )
                send_message(chat_id, reply, reply_to=msg_id)
            else:
                AI_STATE[chat_id] = "ai_text"
                send_message(chat_id, "🧠 لطفاً سوالت رو بفرست:", reply_to=msg_id)
            return

        if text.startswith("/img"):
            arg = text[4:].strip()
            if arg:
                url = f"https://image.pollinations.ai/prompt/{arg.replace(' ', '%20')}"
                send_message(chat_id, f"🖼️ تصویر ساخته شد:\n{url}", reply_to=msg_id)
            else:
                AI_STATE[chat_id] = "ai_image"
                send_message(chat_id, "🖼️ موضوع تصویر چیست؟", reply_to=msg_id)
            return

        if text.startswith("/video"):
            arg = text[6:].strip()
            if arg:
                url = f"https://api.memegen.link/images/custom/{arg.replace(' ', '_')}.gif?background=https://i.imgur.com/8pQe9Qp.jpeg"
                send_message(chat_id, f"🎬 ویدیو ساخته شد:\n{url}", reply_to=msg_id)
            else:
                AI_STATE[chat_id] = "ai_video"
                send_message(chat_id, "🎬 موضوع ویدیو چیست؟", reply_to=msg_id)
            return

        if text == "/panel":
            keyboard = [
                [
                    {"text": "🔄 تمدید سرویس", "data": "renew"},
                    {"text": "📊 آمار کامل", "data": "stats"}
                ],
                [
                    {"text": "🔙 بازگشت", "data": "help"}
                ]
            ]
            send_message(chat_id, "📊 پنل کاربری:\n\n🟢 وضعیت: فعال\n👤 کاربر: عمومی\n⏳ زمان باقی‌مانده: نامحدود\n📈 تعداد درخواست‌ها: 0", 
                        reply_to=msg_id, inline_keyboard=keyboard)
            return

        # برای پیام‌های معمولی هم کیبورد بفرست
        if text.lower() in ["منو", "menu", "دکمه", "کیبورد"]:
            keyboard = [
                [
                    {"text": "🧠 چت AI", "data": "ai_chat"},
                    {"text": "🖼️ تصویر", "data": "ai_image"}
                ],
                [
                    {"text": "🎬 ویدیو", "data": "ai_video"},
                    {"text": "📋 راهنما", "data": "help"}
                ]
            ]
            send_message(chat_id, "🔘 منوی اصلی:", reply_to=msg_id, inline_keyboard=keyboard)
            return

        # پاسخ هوش مصنوعی به پیام‌های عادی
        send_message(chat_id, "⏳ در حال پردازش...", reply_to=msg_id)
        reply = g4f.ChatCompletion.create(
            model=g4f.models.gpt_4,
            messages=[{"role": "user", "content": text}]
        )
        send_message(chat_id, reply, reply_to=msg_id)

    except Exception as e:
        print("[handle_message error]", e)

def main():
    last_offset = None
    set_bot_commands()
    
    # اضافه کردن هندلر برای CallbackQuery
    print("✅ ربات با قابلیت کیبورد اینلاین آماده است...")

    while True:
        updates = get_updates(offset=last_offset)
        messages = updates.get("updates", [])
        last_offset = updates.get("next_offset_id", last_offset)

        for msg in messages:
            if msg.get("type") == "CallbackQuery":
                handle_callback_query(msg)
            elif msg.get("type") == "NewMessage":
                handle_message(msg)

        time.sleep(1)

if __name__ == "__main__":
    main()