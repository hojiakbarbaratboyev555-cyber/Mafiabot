import logging
import random
import os

from fastapi import FastAPI, Request
import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# ======================================================
# LOGGING
# ======================================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ======================================================
# TOKEN
# ======================================================

BOT_TOKEN = os.environ.get("8401348680:AAFFA_EqERcQu-AKUAXlkKpi4WuIh-TUiK8")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN topilmadi!")

# ======================================================
# WEBHOOK
# ======================================================

WEBHOOK_HOST = "https://YOUR-BOT.onrender.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

PORT = int(os.environ.get("PORT", 10000))

# ======================================================
# ROLLAR
# ======================================================

ROLES = {
    "mafia": {
        "name": "🔴 Mafiya",
        "description": "Siz Mafiyasiz!\nKechasi jamoa bilan birgalikda bir kishini o'ldirasiz.",
        "team": "mafia"
    },

    "don": {
        "name": "🔴 Don",
        "description": "Siz Don siz!\nMafiya bossi.",
        "team": "mafia"
    },

    "citizen": {
        "name": "🟢 Tinch aholi",
        "description": "Siz Tinch aholisiz!",
        "team": "citizen"
    },

    "sheriff": {
        "name": "🔵 Komissar",
        "description": "Siz Komissarsiz!",
        "team": "citizen"
    },

    "sergeant": {
        "name": "🔵 Serjant",
        "description": "Siz Serjant siz!",
        "team": "citizen"
    },

    "doctor": {
        "name": "⚪ Shifokor",
        "description": "Siz Shifokorsiz!",
        "team": "citizen"
    },

    "maniac": {
        "name": "⚫ Maniac",
        "description": "Siz Maniaksiz!",
        "team": "maniac"
    },
}

# ======================================================
# ROLE DISTRIBUTION
# ======================================================

def get_roles_for_count(count: int):

    if count == 4:
        return ["mafia", "sheriff", "doctor", "citizen"]

    elif count == 5:
        return ["mafia", "sheriff", "doctor", "citizen", "citizen"]

    elif count == 6:
        return ["mafia", "mafia", "sheriff", "doctor", "citizen", "citizen"]

    elif count == 7:
        return [
            "mafia",
            "mafia",
            "sheriff",
            "doctor",
            "sergeant",
            "citizen",
            "citizen"
        ]

    elif count == 8:
        return [
            "mafia",
            "mafia",
            "don",
            "sheriff",
            "doctor",
            "sergeant",
            "citizen",
            "citizen"
        ]

    elif count <= 10:
        return [
            "mafia",
            "mafia",
            "don",
            "sheriff",
            "doctor",
            "sergeant",
            "maniac"
        ] + ["citizen"] * (count - 7)

    elif count <= 15:
        return [
            "mafia",
            "mafia",
            "mafia",
            "don",
            "sheriff",
            "doctor",
            "sergeant",
            "maniac"
        ] + ["citizen"] * (count - 8)

    else:
        return [
            "mafia",
            "mafia",
            "mafia",
            "don",
            "don",
            "sheriff",
            "doctor",
            "sergeant",
            "maniac"
        ] + ["citizen"] * (count - 9)

# ======================================================
# GAME STORAGE
# ======================================================

games = {}

def new_game(chat_id):

    return {
        "chat_id": chat_id,
        "status": "registration",
        "players": {},
        "message_id": None
    }

# ======================================================
# HELPERS
# ======================================================

def players_list_text(game):

    players = game["players"]

    if not players:
        return "Hozircha hech kim yo'q."

    names = [p["name"] for p in players.values()]

    return "\n".join(
        f"{i+1}. {name}"
        for i, name in enumerate(names)
    )

def registration_text(game):

    count = len(game["players"])

    return (
        "📋 Ro'yxatdan o'tish davom etmoqda\n\n"
        f"{players_list_text(game)}\n\n"
        f"👥 Jami: {count} ta odam"
    )

def join_button(bot_username, chat_id):

    url = f"https://t.me/{bot_username}?start=join_{chat_id}"

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Qo'shilish",
                url=url
            )
        ]
    ])

async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    admins = await context.bot.get_chat_administrators(chat_id)

    return any(admin.user.id == user_id for admin in admins)

# ======================================================
# /game
# ======================================================

async def cmd_game(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat

    if chat.type == "private":

        await update.message.reply_text(
            "Bu komanda faqat guruhda ishlaydi."
        )
        return

    chat_id = chat.id

    if chat_id in games:

        await update.message.reply_text(
            "O'yin allaqachon mavjud."
        )
        return

    games[chat_id] = new_game(chat_id)

    text = registration_text(games[chat_id])

    keyboard = join_button(
        context.bot.username,
        chat_id
    )

    msg = await update.message.reply_text(
        text,
        reply_markup=keyboard
    )

    games[chat_id]["message_id"] = msg.message_id

# ======================================================
# /start
# ======================================================

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user
    args = context.args

    if (
        chat.type == "private"
        and args
        and args[0].startswith("join_")
    ):

        try:
            group_chat_id = int(
                args[0].split("_")[1]
            )

        except:
            await update.message.reply_text(
                "Noto'g'ri havola."
            )
            return

        if group_chat_id not in games:

            await update.message.reply_text(
                "O'yin topilmadi."
            )
            return

        game = games[group_chat_id]

        if game["status"] != "registration":

            await update.message.reply_text(
                "Ro'yxatdan o'tish tugagan."
            )
            return

        if user.id in game["players"]:

            await update.message.reply_text(
                "Siz allaqachon qo'shilgansiz."
            )
            return

        game["players"][user.id] = {
            "name": user.first_name,
            "role": None,
            "alive": True
        }

        try:

            await context.bot.edit_message_text(
                chat_id=group_chat_id,
                message_id=game["message_id"],
                text=registration_text(game),
                reply_markup=join_button(
                    context.bot.username,
                    group_chat_id
                )
            )

        except:
            pass

        await update.message.reply_text(
            "🎉 O'yinga qo'shildingiz."
        )

        return

    # GROUP START

    if chat.type in ["group", "supergroup"]:

        if not await is_admin(update, context):

            await update.message.reply_text(
                "Faqat admin boshlaydi."
            )
            return

        chat_id = chat.id

        if chat_id not in games:

            await update.message.reply_text(
                "Avval /game yozing."
            )
            return

        game = games[chat_id]

        count = len(game["players"])

        if count < 4:

            await update.message.reply_text(
                "Kamida 4 ta o'yinchi kerak."
            )
            return

        roles = get_roles_for_count(count)

        random.shuffle(roles)

        for i, (uid, player) in enumerate(game["players"].items()):

            player["role"] = roles[i]

        game["status"] = "started"

        await update.message.reply_text(
            "🎮 O'yin boshlandi!"
        )

        for uid, player in game["players"].items():

            role = ROLES[player["role"]]

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🎭 Rolni ko'rish",
                        callback_data=f"role_{chat_id}_{uid}"
                    )
                ]
            ])

            try:

                await context.bot.send_message(
                    chat_id=uid,
                    text="🎮 O'yin boshlandi!",
                    reply_markup=keyboard
                )

            except Exception as e:

                logger.warning(
                    f"PM yuborilmadi {uid}: {e}"
                )

# ======================================================
# /leave
# ======================================================

async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat = update.effective_chat
    user = update.effective_user

    if chat.type == "private":
        return

    chat_id = chat.id

    if chat_id not in games:

        await update.message.reply_text(
            "O'yin mavjud emas."
        )
        return

    game = games[chat_id]

    if user.id not in game["players"]:

        await update.message.reply_text(
            "Siz o'yinda emassiz."
        )
        return

    del game["players"][user.id]

    await update.message.reply_text(
        f"{user.first_name} chiqib ketdi."
    )

# ======================================================
# CALLBACK
# ======================================================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    data = query.data

    if data.startswith("role_"):

        parts = data.split("_")

        chat_id = int(parts[1])
        uid = int(parts[2])

        if query.from_user.id != uid:

            await query.answer(
                "Bu sizning rolingiz emas.",
                show_alert=True
            )
            return

        game = games.get(chat_id)

        if not game:
            return

        player = game["players"].get(uid)

        if not player:
            return

        role = ROLES[player["role"]]

        await query.message.reply_text(
            f"{role['name']}\n\n{role['description']}"
        )

# ======================================================
# APP
# ======================================================

application = Application.builder().token(BOT_TOKEN).build()

application.add_handler(CommandHandler("game", cmd_game))
application.add_handler(CommandHandler("start", cmd_start))
application.add_handler(CommandHandler("leave", cmd_leave))
application.add_handler(CallbackQueryHandler(callback_handler))

# ======================================================
# FASTAPI
# ======================================================

app = FastAPI()

@app.on_event("startup")
async def startup():

    await application.initialize()
    await application.start()

    await application.bot.set_webhook(
        WEBHOOK_URL
    )

    logger.info("Webhook o'rnatildi.")

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):

    data = await request.json()

    update = Update.de_json(
        data,
        application.bot
    )

    await application.process_update(update)

    return {"ok": True}

@app.get("/")
async def home():

    return {
        "status": "running"
    }

# ======================================================
# RUN
# ======================================================

if __name__ == "__main__":

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT
    )
