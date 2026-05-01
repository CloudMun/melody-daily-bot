import json
import os
from datetime import datetime, timedelta
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
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] → Попытка отправки медитации на {today}")
   
    try:
        with open('meditations.json', 'r', encoding='utf-8') as f:
            content = f.read().strip()
            meditations = json.loads(content)
       
        text = meditations.get(today)
        if not text:
            text = f"🌿 Медитация на {today} ещё не добавлена."

        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
        print(f"✅ УСПЕШНО ОТПРАВЛЕНО {today}")
        return True

    except json.JSONDecodeError as e:
        error_msg = f"❌ ОШИБКА JSON в meditations.json!\nСтрока {e.lineno}, символ {e.colno}\n{e.msg}"
        print(error_msg)
        await bot.send_message(
            chat_id=CHAT_ID,
            text=f"⚠️ Ошибка в файле meditations.json\n\nНе удалось отправить медитацию на {today}\n\nПроверьте запятые и формат JSON!"
        )
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False


async def scheduler():
    print("🤖 Планировщик запущен...")
    
    last_sent_date = None

    while True:
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # === Логика отправки ===
        should_send = False

        # Если сегодня ещё не отправляли
        if last_sent_date != today_str:
            # Отправляем если сейчас 10:00 или уже позже 10:00
            if now.hour > 10 or (now.hour == 10 and now.minute >= 0):
                should_send = True

        if should_send:
            success = await send_meditation()
            if success:
                last_sent_date = today_str
                print(f"📅 Отправка на {today_str} зафиксирована")

        # Логируем следующее время отправки
        if last_sent_date != today_str:
            next_send = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            if now.hour >= 10:
                next_send += timedelta(days=1)
            minutes_left = int((next_send - now).total_seconds() / 60)
            print(f"⏰ Следующая отправка: завтра в 10:00 (через ~{minutes_left//60}ч {minutes_left%60}мин)")

        await asyncio.sleep(30)


# ================== ЗАПУСК ==================
if __name__ == "__main__":
    print(f"🚀 Бот запущен | Порт: {PORT} | Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
