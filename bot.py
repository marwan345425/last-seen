import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from datetime import datetime, timedelta
import pytz

# ------- بيانات حسابك -------
api_id = 22575615
api_hash = "c77e3b35d6b1b2b35b35020d69077d8d"
string_session = "1BJWap1wBu0CfmMUBcv72WTVUxj6Jsss6HkTa0__H9QKMba8_koRYey8g8_uuvw4tDyRKyhR2IG__TioSbXQYr1J8KJ0xUJmBdhf2Eel8-zrsYIUtK2j4aTEiDgpduNxbtVNws5qKwpGonE-LpgawNhNZzFTwUeEVBSG1lrTFDHwFsiHWoiUFqOsGpw4098uMEl2_GzfxD3_sEGPnHQzHsg0uWj2KtxgzRkuEg8a8vEBGTAZnNUJQ2hTjfBCoLTLxKzjLiOUSa5b9zGsn_VFmgG0to6ww2hJfwbhfZ9l3aBVHJWgZmCQXvKDzboeYIPcOhM7HDT3Vx8efvFuVj8b3zWbe6_HPyNs="
notify_user = "@Leeo71"      # اليوزر اللي يستقبل التنبيهات
target_user = "Kh770l" # الشخص اللي تبي تراقبه (اكتب اليوزر بدون @)

# ------- الإعدادات -------
check_interval = 30   # كل 30 ثانية مراقبة
health_interval = 3600  # كل ساعة تقرير تشغيل

# ------- التوقيت -------
ksa = pytz.timezone("Asia/Riyadh")

client = TelegramClient(StringSession(string_session), api_id, api_hash)

last_online_status = None
last_message_ids = {}   # لمنع التكرار في رسائل القروبات
last_private_id = None  # آخر رسالة خاصة

async def send_health_message():
    now = datetime.now(ksa).strftime("%Y-%m-%d %I:%M:%S %p")
    msg = f"👾 البوت شغال - {now} (توقيت المدينة المنورة)"
    try:
        await client.send_message(notify_user, msg)
    except:
        pass

async def monitor_user():
    global last_online_status, last_message_ids, last_private_id

    await client.start()
    target = await client.get_entity(target_user)

    print("Bot started successfully.")

    last_health_time = datetime.now()

    while True:
        now = datetime.now()

        # -------- تقرير كل ساعة --------
        if now - last_health_time >= timedelta(seconds=health_interval):
            await send_health_message()
            last_health_time = now

        # -------- مراقبة آخر ظهور --------
        try:
            status = target.status
            readable_status = None

            if hasattr(status, "was_online"):
                readable_status = "offline"
            elif "Online" in str(status):
                readable_status = "online"
            else:
                readable_status = "hidden"

            if readable_status != last_online_status:
                last_online_status = readable_status
                await client.send_message(
                    notify_user, 
                    f"👤 {target.first_name} صار الآن: {readable_status}"
                )
        except:
            pass

        # -------- مراقبة رسائل الخاص --------
        try:
            async for msg in client.iter_messages(target, limit=1):
                if msg.id != last_private_id:
                    last_private_id = msg.id
                    await client.send_message(
                        notify_user,
                        f"📩 رسالة جديدة من {target.first_name} في الخاص:\n\n{msg.text}"
                    )
        except:
            pass

        # -------- مراقبة رسائل القروبات --------
        dialogs = await client.get_dialogs()
        for dialog in dialogs:
            entity = dialog.entity
            try:
                async for msg in client.iter_messages(entity, limit=3):
                    if msg.sender_id == target.id:
                        if last_message_ids.get(entity.id) != msg.id:
                            last_message_ids[entity.id] = msg.id
                            await client.send_message(
                                notify_user,
                                f"💬 {target.first_name} كتب في قروب ({entity.title}):\n\n{msg.text}"
                            )
            except:
                continue

        await asyncio.sleep(check_interval)

async def main():
    await monitor_user()

if __name__ == "__main__":
    asyncio.run(main())
