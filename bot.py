import json
from datetime import datetime
import telegram
import asyncio
import os

# ================== НАСТРОЙКИ ==================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TEST_MODE = os.getenv("TEST_MODE", "false").lower() == "true"
# ================================================

if not TOKEN or not CHAT_ID:
    print("❌ Ошибка: TOKEN или CHAT_ID не найдены!")
    exit(1)

bot = telegram.Bot(token=TOKEN)

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

async def main():
    print("🤖 Бот успешно запущен на Railway!")
    
    if TEST_MODE:
        print("🧪 TEST_MODE включён — отправляем прямо сейчас...")
        await send_meditation()
        print("✅ Тест завершён. Можешь отключить TEST_MODE.")
        return
    
    # Обычный режим
    while True:
        now = datetime.now()
        if now.hour == 10 and now.minute == 0:   # 10:00 Москва
            await send_meditation()
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
