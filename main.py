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
    print(f"[{datetime.now()}] → Отправка медитации на {today}")
   
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
        print(f"❌ Ошибка отправки: {e}")
        return False


async def scheduler():
    print("🤖 Планировщик запущен...")

    while True:
        now = datetime.now()
        
        if now.hour == 10 and now.minute == 0:
            await send_meditation()
        
        await asyncio.sleep(60)

    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:
            await send_meditation()
        
        await asyncio.sleep(60)


# ================== ЗАПУСК ==================
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
