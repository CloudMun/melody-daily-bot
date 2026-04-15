import json
from datetime import datetime
import telegram
import asyncio
import os

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    print("❌ Ошибка: TOKEN или CHAT_ID не найдены в Variables!")
    exit(1)
# ================================================

bot = telegram.Bot(token=TOKEN)

async def send_daily():
    today = datetime.now().strftime("%m-%d")
    print(f"[{datetime.now()}] → Попытка отправить медитацию на {today}")
    
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
    print("🤖 Бот успешно запущен на Railway!")
    while True:
        now = datetime.now()
        # 10:00 по Москве
        if now.hour == 10 and now.minute == 0:
            await send_daily()
        
        await asyncio.sleep(60)  # проверка каждую минуту

if __name__ == "__main__":
    asyncio.run(main())
