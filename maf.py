import os
import asyncio
from fastapi import FastAPI
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import uvicorn
from datetime import datetime, timedelta

BOT_TOKEN = "8231459467:AAHtetAaCv2BjMtzk9lxXO5KBbvwlWsdUrk"
GROUP_ID = -1001234567890
ADMIN_ID = 8297497276

MIN_PLAYERS = 4
MAX_PLAYERS = 25
NIGHT_DURATION = 45
DAY_DURATION = 45
MAX_ROLE_ATTEMPTS = 3

players = {}
votes = {}
roles = {}
ROLE_LIST = [
    "👨🏼 Tinch axoli", "👨🏼‍⚕️ Shifokor", "🧙🏼‍♂ Daydi", "🕵🏻‍♂ Komissar",
    "💣 Kamikaze", "💃 Kezuvchi", "👮🏻‍♂ Serjant", "🔪 Qotil",
    "⚡️ Koldun", "🤵🏻 Don", "🤵🏼 Mafia", "👨🏼‍💼 Advokat",
    "🦇 Ayg‘oqchi", "👨‍🔬 Labarant", "☠️ Minior", "👨🏻‍🎤 Snayperchi",
    "🏹 Kamonchi", "🦎 Sotqin"
]

# ---------------- FastAPI -----------------
app = FastAPI()

@app.get("/")
async def home():
    return {"status": "Mafiabot ishlayapti!"}

# ---------------- Aiogram -----------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.from_user.id not in players:
        players[message.from_user.id] = {
            "username": message.from_user.username or message.from_user.full_name,
            "name": message.from_user.full_name,
            "alive": True,
            "role_attempts": 0,
            "has_voted": False,
            "coin": 0
        }
    await message.answer("👋 Real MaFia botga xush kelibsiz! /profile bilan profilni ko'ring")

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    p = players.get(message.from_user.id, None)
    if p:
        await message.answer(f"👤 Profil:\nCoin: {p['coin']}\nAlive: {p['alive']}")
    else:
        await message.answer("❌ Siz botda ro'yxatdan o'tmagansiz.")

# Tun/kun, ovoz berish, ro‘llar va inline tugmalar shu yerga qo‘shiladi

# ---------------- Main -----------------
async def main():
    polling = dp.start_polling(bot)
    port = int(os.environ.get("PORT", 8000))
    server = uvicorn.Server(uvicorn.Config(app=app, host="0.0.0.0", port=port, log_level="info"))
    await asyncio.gather(polling, server.serve())

if __name__ == "__main__":
    asyncio.run(main())
