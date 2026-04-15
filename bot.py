import json
from datetime import datetime
import telegram
import asyncio

# ================== ТВОИ ДАННЫЕ ==================
TOKEN = "8748026062:AAHjTihiLCj5p8JPMOREhGmUf4HxS_AJV1A"
CHAT_ID = "-1002383860662"
# ================================================

bot = telegram.Bot(token=TOKEN)

async def send_daily_meditation():
    today = datetime.now().strftime("%m-%d")
    print(f"[{datetime.now()}] Запуск для даты: {today}")
    
    try:
        with open('meditations.json', 'r', encoding='utf-8') as f:
            meditations = json.load(f)
        
        text = meditations.get(today)
        
        if not text:
            text = f"🌿 Медитация на {today} ещё не добавлена."
        
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='HTML')
        print(f"✅ Успешно отправлено {today}")
        
    except Exception as e:
        print(f"❌ ОШИБКА: {e}")

def main():
    asyncio.run(send_daily_meditation())

if __name__ == "__main__":
    main()
