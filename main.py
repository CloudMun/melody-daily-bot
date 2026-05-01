import json
import os
from datetime import datetime
import asyncio
import telegram
from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PORT = int(os.getenv("PORT", 8000))

if not TOKEN or not CHAT_ID:
    print("❌ Ошибка: TOKEN или CHAT_ID не найдены!")
    exit(1)

bot = telegram.Bot(token=TOKEN)

# ================== LIFESPAN ==================
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(scheduler())
    print("✅ Планировщик успешно запущен в фоне")
    yield
    print("🛑 Бот останавливается...")

app = FastAPI(lifespan=lifespan)

# ================== HEALTH ENDPOINT ==================
@app.get("/health")
@app.head("/health")
async def health():
    return {
        "status": "alive",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ================== ОСНОВНЫЕ ФУНКЦИИ ==================
async def send_meditation():
    today = datetime.now().strftime("%m-%d")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] → Отправка медитации на {today}")
   
    try:
        with open('meditations.json', 'r', encoding='utf-8') as f:
            meditations = json.load(f)
       
        text = meditations.get(today)
        if not text:
            text = f"🌿 Медитация на {today} ещё не добавлена."

        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
        print(f"✅ УСПЕШНО ОТПРАВЛЕНО {today}")
        return True
    except Exception as e:
        print(f"❌ Ошибка при отправке медитации: {e}")
        return False


async def scheduler():
    print("🤖 Планировщик запущен...")
    
    last_sent_date = None                     # Защита от повторной отправки
    print(f"⏰ Следующая отправка ожидается сегодня в 10:00")

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # Отправляем в 10:00, если сегодня ещё не отправляли
        if now.hour == 10 and now.minute == 0 and last_sent_date != today_str:
            success = await send_meditation()
            if success:
                last_sent_date = today_str
                print(f"📅 Отправка на {today_str} успешно зафиксирована")

        # Проверка каждые 30 секунд
        await asyncio.sleep(30)


# ================== ЗАПУСК ==================
if __name__ == "__main__":
    print(f"🚀 Бот запущен | Порт: {PORT} | Время запуска: {datetime.now()}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
