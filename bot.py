import json
import os
from datetime import datetime
import asyncio
import telegram
from fastapi import FastAPI
import uvicorn

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
PORT = int(os.getenv("PORT", 8000))          # ← Важно для Railway

# ================================================
if not TOKEN or not CHAT_ID:
    print("❌ Ошибка: TOKEN или CHAT_ID не найдены!")
    exit(1)

bot = telegram.Bot(token=TOKEN)

app = FastAPI()

@app.get("/health")
async def health():
    return {
        "status": "alive",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_mode": TEST_MODE
    }

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
    
    if TEST_MODE:
        print("🧪 TEST_MODE включён — отправляем прямо сейчас...")
        await send_meditation()
        return

    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:
            await send_meditation()
        
        await asyncio.sleep(60)


async def main():
    print(f"🤖 Бот запущен на Railway! Порт: {PORT}")
    
    # Запускаем планировщик и веб-сервер одновременно
    await asyncio.gather(
        scheduler(),
        uvicorn.Server(uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="info")).serve()
    )


if __name__ == "__main__":
    asyncio.run(main())
