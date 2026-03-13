import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime, timedelta
import uvicorn

# ---------------- CONFIG -----------------
BOT_TOKEN = "8231459467:AAHtetAaCv2BjMtzk9lxXO5KBbvwlWsdUrk"
ADMIN_ID = 8297497276
GROUP_ID = -1001234567890  # O'yin guruh ID sini bu yerga qo'yish

MIN_PLAYERS = 4
MAX_PLAYERS = 25
NIGHT_DURATION = 45   # sekund
DAY_DURATION = 45     # sekund
MAX_ROLE_ATTEMPTS = 3

# ---------------- GLOBAL DATA -----------------
players = {}  # foydalanuvchi ma'lumotlari
votes = {}    # ovozlar
roles = {}    # ro'llar

ROLE_LIST = [
    "👨🏼 Tinch axoli", "👨🏼‍⚕️ Shifokor", "🧙🏼‍♂ Daydi", "🕵🏻‍♂ Komissar",
    "💣 Kamikaze", "💃 Kezuvchi", "👮🏻‍♂ Serjant", "🔪 Qotil",
    "⚡️ Koldun", "🤵🏻 Don", "🤵🏼 Mafia", "👨🏼‍💼 Advokat",
    "🦇 Ayg‘oqchi", "👨‍🔬 Labarant", "☠️ Minior", "👨🏻‍🎤 Snayperchi",
    "🏹 Kamonchi", "🦎 Sotqin"
]

# ----------------- UTILS -----------------
def can_start_game():
    n = len(players)
    if n < MIN_PLAYERS:
        return False, f"O'yin boshlanishi uchun kamida {MIN_PLAYERS} o'yinchi kerak!"
    elif n > MAX_PLAYERS:
        return False, f"O'yin boshlanishi uchun maksimal {MAX_PLAYERS} o'yinchi bo'lishi mumkin!"
    return True, "O'yin boshlash mumkin!"

async def night_phase():
    await bot.send_message(GROUP_ID, "🌙 Tun boshlandi! Rolingizni ishlating.")
    for user_id in players:
        players[user_id]["role_attempts"] = 0

    start_time = datetime.now()
    end_time = start_time + timedelta(seconds=NIGHT_DURATION)

    while datetime.now() < end_time:
        for user_id, data in players.items():
            if data["alive"] and data["role_attempts"] >= MAX_ROLE_ATTEMPTS:
                data["alive"] = False
                await bot.send_message(user_id, f"💀 @{data['username']}, siz tun davomida rolingizni ishlatmadingiz, o'yindan chiqarildingiz!")
        await asyncio.sleep(1)

    await bot.send_message(GROUP_ID, "🌙 Tun tugadi, kun boshlanmoqda!")
    await day_phase()

async def day_phase():
    await bot.send_message(GROUP_ID, "☀️ Kun boshlandi! Ovoz berish 45 sek davom etadi.")
    for user_id in players:
        players[user_id]["has_voted"] = False
    votes.clear()
    await asyncio.sleep(DAY_DURATION)

    # Ovozlarni hisoblash
    if votes:
        winner = max(votes, key=votes.get)
        await bot.send_message(GROUP_ID, f"🗳 Ovoz berish tugadi! Natija: @{players[winner]['username']}")
    else:
        await bot.send_message(GROUP_ID, "🗳 Hech kim ovoz bermadi.")

    await night_phase()

def use_role(user_id):
    if players[user_id]["alive"]:
        players[user_id]["role_attempts"] += 1
        if players[user_id]["role_attempts"] > MAX_ROLE_ATTEMPTS:
            players[user_id]["alive"] = False

async def vote_callback(user_id, choice):
    if players[user_id]["has_voted"]:
        await bot.send_message(user_id, "❌ Siz allaqachon ovoz berdingiz!")
        return
    players[user_id]["has_voted"] = True
    votes[choice] = votes.get(choice, 0) + 1
    await bot.send_message(user_id, f"✅ @{players[user_id]['username']} siz {choice} ga ovoz berdingiz!")

# ----------------- BOT HANDLERS -----------------
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
            "coin": 0,
            "diamond": 0
        }
    await message.answer("👋 Real MaFia botga xush kelibsiz! My Profile uchun /profile deb yozing.")

@dp.message(Command("profile"))
async def cmd_profile(message: types.Message):
    p = players.get(message.from_user.id, None)
    if p:
        await message.answer(f"👤 Profilingiz:\nCoin: {p['coin']}\nDiamond: {p['diamond']}\nAlive: {p['alive']}")
    else:
        await message.answer("❌ Siz botda ro'yxatdan o'tmagansiz.")

async def send_role_keyboard(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=role, callback_data=f"role_{i}")] for i, role in enumerate(ROLE_LIST)
    ])
    await bot.send_message(user_id, "Rolingizni tanlang:", reply_markup=keyboard)

# ----------------- PORT CONFIG FOR RENDER -----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:dp", host="0.0.0.0", port=port, reload=True)
