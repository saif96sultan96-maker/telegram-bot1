from telethon import TelegramClient, events
import asyncio, threading, time, os

# ===== بيانات حسابك =====
api_id = 30188495
api_hash = '9e2b2efaf1f57a3277e23d7abfc73fd3'
phone = '+9647868499043'

client = TelegramClient('session', api_id, api_hash)
channels = {}  # لتخزين بيانات القنوات

# ===== دالة الإرسال التلقائي =====
def send_messages(chat_id):
    while True:
        data = channels.get(chat_id)
        if not data or data.get('stop', False):
            break
        msg = data.get('message','رسالة تلقائية')
        img_file = data.get('image', None)
        interval = data.get('interval', 180)
        try:
            if img_file and os.path.exists(img_file):
                asyncio.run(client.send_file(chat_id, img_file, caption=msg))
            else:
                asyncio.run(client.send_message(chat_id, msg))
        except Exception as e:
            print(f"فشل الإرسال للقناة {chat_id}: {e}")
        time.sleep(interval)

# ===== استقبال الرسائل =====
@client.on(events.NewMessage)
async def handle_text(event):
    text = event.message.message.strip()

    # ----- إضافة قناة -----
    if text.startswith("أضف قناة"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await event.respond("الرجاء كتابة: أضف قناة @اسم_القناة")
            return
        channel_name = parts[2].strip()
        if not channel_name.startswith('@'):
            await event.respond("اسم القناة يجب أن يبدأ بـ @")
            return
        if channel_name in channels:
            await event.respond(f"القناة {channel_name} موجودة مسبقاً!")
        else:
            channels[channel_name] = {'message':'رسالة تلقائية','image':None,'interval':180,'thread':None,'stop':False}
            await event.respond(f"تمت إضافة القناة {channel_name} ✅")

    # ----- رفع صورة -----
    elif text.startswith("رفع صورة"):
        if event.is_reply and event.photo:
            reply_msg = await event.get_reply_message()
            channel_name = reply_msg.message.strip()
            if channel_name in channels:
                path = f"{channel_name.replace('@','')}.jpg"
                await event.download_media(path)
                channels[channel_name]['image'] = path
                await event.respond(f"تم ربط الصورة بالقناة {channel_name} ✅")
            else:
                await event.respond("القناة غير موجودة! أضف القناة أولاً.")
        else:
            await event.respond("الرجاء إرسال الصورة كرد على اسم القناة")

    # ----- تعديل نص -----
    elif text.startswith("عدل نص"):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            await event.respond("الرجاء كتابة: عدل نص @اسم_القناة الرسالة الجديدة")
            return
        channel_name = parts[1].strip()
        new_msg = parts[2].strip()
        if channel_name in channels:
            channels[channel_name]['message'] = new_msg
            await event.respond(f"تم تعديل النص للقناة {channel_name} ✅")
        else:
            await event.respond("القناة غير موجودة!")

    # ----- ضبط الفترة -----
    elif text.startswith("ضبط فترة"):
        parts = text.split()
        if len(parts) < 3:
            await event.respond("الرجاء كتابة: ضبط فترة 5 @اسم_القناة")
            return
        try:
            interval = int(parts[2]) * 60
            channel_name = parts[3]
            if channel_name in channels:
                channels[channel_name]['interval'] = interval
                await event.respond(f"تم ضبط الفترة للقناة {channel_name} كل {parts[2]} دقيقة ✅")
            else:
                await event.respond("القناة غير موجودة!")
        except:
            await event.respond("تأكد من كتابة الرقم بشكل صحيح")

    # ----- بدء الإرسال -----
    elif text == "ابدأ الإرسال":
        for cid, ch_data in channels.items():
            if not ch_data.get('thread'):
                t = threading.Thread(target=send_messages, args=(cid,), daemon=True)
                t.start()
                channels[cid]['thread'] = t
                channels[cid]['stop'] = False
        await event.respond("تم بدء الإرسال التلقائي ✅")

    # ----- إيقاف الإرسال -----
    elif text == "أوقف الإرسال":
        for cid in channels:
            channels[cid]['stop'] = True
        await event.respond("تم إيقاف الإرسال التلقائي ✅")

# ===== تشغيل البوت =====
async def main():
    await client.start(phone)
    me = await client.get_me()
    print(f"تم تسجيل الدخول بحساب {me.username}!")
    await client.run_until_disconnected()

asyncio.run(main())