import json
from datetime import datetime
import telegram
import asyncio
import os
import time

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("8748026062:AAHjTihiLCj5p8JPMOREhGmUf4HxS_AJV1A")
CHAT_ID = os.getenv("-1002383860662")
# ==============================================

bot = telegram.Bot(token=TOKEN)

async def send_daily():
    today = datetime.now().strftime("%m-%d")
    print(f"[{datetime.now()}] → Отправка медитации на {today}")
    
    try:
        with open('meditations.json', 'r', encoding='utf-8') as f:
            meditations = json.load(f)
        
        text = meditations.get(today)
        if not text:
            text = f"🌿 Медитация на {today} ещё не добавлена."

        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
        print(f"✅ Успешно отправлено {today}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

async def main():
    print("🤖 Бот запущен на Railway...")
    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:   # 10:00 по Москве (Railway — UTC+3)
            await send_daily()
        
        await asyncio.sleep(60)  # проверка каждую минуту

if __name__ == "__main__":
    asyncio.run(main())
