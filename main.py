# ================== ВЕБ-СЕРВЕР И ПЛАНИРОВЩИК ==================
import uvicorn
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск планировщика при старте
    asyncio.create_task(scheduler())
    print("✅ Планировщик запущен в фоне")
    yield
    print("🛑 Бот останавливается...")

# Создаём FastAPI с lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {
        "status": "alive",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "test_mode": TEST_MODE
    }


async def scheduler():
    print("🤖 Планировщик запущен...")
    
    if TEST_MODE:
        print("🧪 TEST_MODE: отправляем медитацию сейчас")
        await send_meditation()
        return

    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:
            await send_meditation()
        
        await asyncio.sleep(60)


# Запуск через uvicorn (Railway)
if __name__ == "__main__":
    uvicorn.run("bot:app", host="0.0.0.0", port=PORT, log_level="info")
