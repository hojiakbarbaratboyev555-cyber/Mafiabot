import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===================== SOZLAMALAR =====================
BOT_TOKEN = "8387661156:AAE7dQc6jRIivvhlACwrC3jGLhfPw8KgK-c"
ADMIN_GROUP_ID = -5168141912  # Admin guruh ID
CHANNEL_ID = "https://t.me/uzb_ads"   # Asosiy kanal username
ADMIN_URL = "https://t.me/HB7410_bot"  # Admin URL
REQUIRED_CHANNEL = "https://t.me/uzb_ads"  # Majburiy obuna kanali

# ===================== HOLATLAR =====================
(
    CHOOSING_TYPE,
    TG_PHOTO, TG_SUBSCRIBERS, TG_PRICE, TG_PHONE, TG_USERNAME, TG_USER_USERNAME,
    IG_PHOTO, IG_LINK, IG_SUBSCRIBERS, IG_PRICE, IG_PHONE, IG_USER_USERNAME,
    GAME_PHOTO, GAME_PRICE, GAME_PHONE, GAME_USER_USERNAME,
) = range(17)

# ===================== MA'LUMOTLAR SAQLASH =====================
user_data_store = {}  # { user_id: { "orders": [...] } }
pending_orders = {}   # { order_id: { ...order data... } }
order_counter = [0]

def new_order_id():
    order_counter[0] += 1
    return order_counter[0]

GAME_TYPES = ["DLS", "FC Mobile", "PUBG", "Freefire", "Efootball", "MLBB", "Boshqa"]

# ===================== OBUNA TEKSHIRISH =====================
async def check_subscription(user_id: int, bot) -> bool:
    try:
        member = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

async def subscription_keyboard():
    keyboard = [
        [InlineKeyboardButton("📢 Kanalga o'tish", url=f"https://t.me/{REQUIRED_CHANNEL.lstrip('@')}")],
        [InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ===================== ASOSIY MENYU =====================
def main_menu_keyboard():
    keyboard = [
        [KeyboardButton("🛒 Buyurtma berish")],
        [KeyboardButton("📦 Akkauntlarim")],
        [KeyboardButton("👨‍💼 Admin bilan bog'lanish")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===================== /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_subscribed = await check_subscription(user.id, context.bot)

    if not is_subscribed:
        await update.message.reply_text(
            "❗ Botdan to'liq foydalanish uchun quyidagi kanalga obuna bo'ling:",
            reply_markup=await subscription_keyboard()
        )
        return

    await update.message.reply_text(
        f"👋 Salom, {user.first_name}!\n\nSiz asosiy menudasiz.",
        reply_markup=main_menu_keyboard()
    )

async def check_sub_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    is_subscribed = await check_subscription(user.id, context.bot)

    if is_subscribed:
        await query.message.edit_text(
            f"✅ Salom, {user.first_name}!\n\nSiz asosiy menudasiz."
        )
        await context.bot.send_message(
            chat_id=user.id,
            text="Asosiy menyu:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await query.message.edit_text(
            "❗ Botdan to'liq foydalanish uchun quyidagi kanalga obuna bo'ling:",
            reply_markup=await subscription_keyboard()
        )

# ===================== BUYURTMA BERISH =====================
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    is_subscribed = await check_subscription(user.id, context.bot)
    if not is_subscribed:
        await update.message.reply_text(
            "❗ Botdan to'liq foydalanish uchun quyidagi kanalga obuna bo'ling:",
            reply_markup=await subscription_keyboard()
        )
        return ConversationHandler.END

    context.user_data.clear()
    keyboard = [
        [KeyboardButton("Telegram"), KeyboardButton("Instagram"), KeyboardButton("DLS")],
        [KeyboardButton("FC Mobile"), KeyboardButton("PUBG"), KeyboardButton("Freefire")],
        [KeyboardButton("Efootball"), KeyboardButton("MLBB"), KeyboardButton("Boshqa")],
        [KeyboardButton("🏠 Asosiy menu")]
    ]
    await update.message.reply_text(
        "📱 Siz o'z akkauntingizni biz bilan birga sotmoqchisiz.\n\nAkkaunt turini tanlang:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )
    return CHOOSING_TYPE

async def choose_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END

    context.user_data["type"] = text

    if text == "Telegram":
        await update.message.reply_text(
            "📸 Kanal yoki Guruh rasmini yuboring:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 Asosiy menu")]], resize_keyboard=True)
        )
        return TG_PHOTO
    elif text == "Instagram":
        await update.message.reply_text(
            "📸 Instagram sahifangiz rasmini yuboring:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 Asosiy menu")]], resize_keyboard=True)
        )
        return IG_PHOTO
    elif text in GAME_TYPES:
        await update.message.reply_text(
            "📸 Akkaunt rasmini yuboring:",
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton("🏠 Asosiy menu")]], resize_keyboard=True)
        )
        return GAME_PHOTO
    else:
        await update.message.reply_text("❌ Noto'g'ri tanlov. Qaytadan tanlang.")
        return CHOOSING_TYPE

# ===================== TELEGRAM =====================
async def tg_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    if not update.message.photo:
        await update.message.reply_text("❗ Iltimos, rasm yuboring.")
        return TG_PHOTO
    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("👥 Obunachilar sonini kiriting:")
    return TG_SUBSCRIBERS

async def tg_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["subscribers"] = update.message.text
    await update.message.reply_text("💰 Narxni kiriting (so'm):")
    return TG_PRICE

async def tg_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["price"] = update.message.text
    await update.message.reply_text(
        "📞 Telefon raqamingizni kiriting:\n\nNamuna: +998901234567"
    )
    return TG_PHONE

async def tg_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    phone = update.message.text.strip()
    import re
    if not re.match(r'^\+998\d{9}$', phone):
        await update.message.reply_text(
            "❗ Telefon raqam noto'g'ri formatda.\n\nNamuna: +998901234567\n\nQaytadan kiriting:"
        )
        return TG_PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("🔗 Kanal username kiriting (masalan: @kanal_nomi):")
    return TG_USERNAME

async def tg_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["channel_username"] = update.message.text
    await update.message.reply_text("👤 Sizning Telegram username ingizni kiriting (masalan: @username):")
    return TG_USER_USERNAME

async def tg_user_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["user_username"] = update.message.text
    await show_order_summary(update, context)
    return ConversationHandler.END

# ===================== INSTAGRAM =====================
async def ig_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    if not update.message.photo:
        await update.message.reply_text("❗ Iltimos, rasm yuboring.")
        return IG_PHOTO
    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("🔗 Instagram sahifa silkasini (link) kiriting:")
    return IG_LINK

async def ig_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["ig_link"] = update.message.text
    await update.message.reply_text("👥 Obunachilar sonini kiriting:")
    return IG_SUBSCRIBERS

async def ig_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["subscribers"] = update.message.text
    await update.message.reply_text("💰 Narxni kiriting (so'm):")
    return IG_PRICE

async def ig_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:\n\nNamuna: +998901234567")
    return IG_PHONE

async def ig_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    phone = update.message.text.strip()
    import re
    if not re.match(r'^\+998\d{9}$', phone):
        await update.message.reply_text(
            "❗ Telefon raqam noto'g'ri formatda.\n\nNamuna: +998901234567\n\nQaytadan kiriting:"
        )
        return IG_PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("👤 Sizning Telegram username ingizni kiriting (masalan: @username):")
    return IG_USER_USERNAME

async def ig_user_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["user_username"] = update.message.text
    await show_order_summary(update, context)
    return ConversationHandler.END

# ===================== O'YIN AKKAUNTLARI =====================
async def game_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    if not update.message.photo:
        await update.message.reply_text("❗ Iltimos, rasm yuboring.")
        return GAME_PHOTO
    context.user_data["photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("💰 Narxni kiriting (so'm):")
    return GAME_PRICE

async def game_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["price"] = update.message.text
    await update.message.reply_text("📞 Telefon raqamingizni kiriting:\n\nNamuna: +998901234567")
    return GAME_PHONE

async def game_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    phone = update.message.text.strip()
    import re
    if not re.match(r'^\+998\d{9}$', phone):
        await update.message.reply_text(
            "❗ Telefon raqam noto'g'ri formatda.\n\nNamuna: +998901234567\n\nQaytadan kiriting:"
        )
        return GAME_PHONE
    context.user_data["phone"] = phone
    await update.message.reply_text("👤 Sizning Telegram username ingizni kiriting (masalan: @username):")
    return GAME_USER_USERNAME

async def game_user_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🏠 Asosiy menu":
        await update.message.reply_text("Asosiy menyu:", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    context.user_data["user_username"] = update.message.text
    await show_order_summary(update, context)
    return ConversationHandler.END

# ===================== BUYURTMA KO'RSATISH =====================
def build_caption(data: dict) -> str:
    acc_type = data.get("type", "")
    caption = f"📋 <b>Buyurtma ma'lumotlari:</b>\n\n"
    caption += f"📱 <b>Tur:</b> {acc_type}\n"

    if acc_type == "Telegram":
        caption += f"👥 <b>Obunachilar:</b> {data.get('subscribers', '')}\n"
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"
        caption += f"📞 <b>Telefon:</b> {data.get('phone', '')}\n"
        caption += f"🔗 <b>Kanal:</b> {data.get('channel_username', '')}\n"
        caption += f"👤 <b>Egasi:</b> {data.get('user_username', '')}\n"
    elif acc_type == "Instagram":
        caption += f"🔗 <b>Sahifa:</b> {data.get('ig_link', '')}\n"
        caption += f"👥 <b>Obunachilar:</b> {data.get('subscribers', '')}\n"
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"
        caption += f"📞 <b>Telefon:</b> {data.get('phone', '')}\n"
        caption += f"👤 <b>Egasi:</b> {data.get('user_username', '')}\n"
    else:
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"
        caption += f"📞 <b>Telefon:</b> {data.get('phone', '')}\n"
        caption += f"👤 <b>Egasi:</b> {data.get('user_username', '')}\n"

    return caption

def build_channel_caption(data: dict) -> str:
    """Kanalga joylash uchun - user va kanal usernamesi yo'q"""
    acc_type = data.get("type", "")
    caption = f"📋 <b>Akkaunt sotuvda:</b>\n\n"
    caption += f"📱 <b>Tur:</b> {acc_type}\n"

    if acc_type == "Telegram":
        caption += f"👥 <b>Obunachilar:</b> {data.get('subscribers', '')}\n"
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"
    elif acc_type == "Instagram":
        caption += f"👥 <b>Obunachilar:</b> {data.get('subscribers', '')}\n"
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"
    else:
        caption += f"💰 <b>Narx:</b> {data.get('price', '')} so'm\n"

    return caption

async def show_order_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data
    user = update.effective_user
    caption = build_caption(data)

    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data="user_confirm"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="user_cancel")
        ]
    ]

    await context.bot.send_photo(
        chat_id=user.id,
        photo=data["photo"],
        caption=caption,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    # Vaqtincha saqlash
    pending_orders[f"tmp_{user.id}"] = {**data, "user_id": user.id}

async def user_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    tmp_key = f"tmp_{user.id}"
    data = pending_orders.get(tmp_key)
    if not data:
        await query.message.reply_text("❌ Buyurtma topilmadi.")
        return

    order_id = new_order_id()
    pending_orders[order_id] = {**data, "message_id": None, "user_id": user.id}
    del pending_orders[tmp_key]

    # Adminga yuborish
    admin_caption = build_caption(data) + f"\n🆔 <b>Buyurtma ID:</b> #{order_id}"
    admin_keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"admin_confirm_{order_id}"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data=f"admin_cancel_{order_id}")
        ]
    ]
    msg = await context.bot.send_photo(
        chat_id=ADMIN_GROUP_ID,
        photo=data["photo"],
        caption=admin_caption,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(admin_keyboard)
    )
    pending_orders[order_id]["admin_msg_id"] = msg.message_id

    await query.message.edit_caption(
        caption=build_caption(data) + "\n\n⏳ <b>Buyurtmangiz adminlarga yuborildi. Kuting...</b>",
        parse_mode="HTML"
    )

async def user_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    tmp_key = f"tmp_{user.id}"
    if tmp_key in pending_orders:
        del pending_orders[tmp_key]
    await query.message.edit_caption(
        caption="❌ Buyurtma bekor qilindi.",
        parse_mode="HTML"
    )
    await context.bot.send_message(chat_id=user.id, text="Asosiy menyu:", reply_markup=main_menu_keyboard())

# ===================== ADMIN TASDIQLASH =====================
async def admin_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[-1])
    data = pending_orders.get(order_id)
    if not data:
        await query.message.reply_text("❌ Buyurtma topilmadi.")
        return

    # Kanalga joylashtirish
    channel_caption = build_channel_caption(data)
    channel_keyboard = [
        [
            InlineKeyboardButton("📢 Kanalni ko'rish", url=f"https://t.me/{CHANNEL_ID.lstrip('@')}"),
            InlineKeyboardButton("🛒 Admin orqali sotib olish", url=ADMIN_URL),
        ],
        [InlineKeyboardButton("👤 Egasidan sotib olish", url=f"https://t.me/{data.get('user_username', '').lstrip('@')}")]
    ]
    channel_msg = await context.bot.send_photo(
        chat_id=CHANNEL_ID,
        photo=data["photo"],
        caption=channel_caption,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(channel_keyboard)
    )

    # Ma'lumotni saqlash (akkauntlarim uchun)
    user_id = data["user_id"]
    if user_id not in user_data_store:
        user_data_store[user_id] = {"orders": []}
    user_data_store[user_id]["orders"].append({
        "order_id": order_id,
        "data": data,
        "channel_msg_id": channel_msg.message_id
    })

    # Foydalanuvchiga xabar
    post_url = f"https://t.me/{CHANNEL_ID.lstrip('@')}/{channel_msg.message_id}"
    view_keyboard = [[InlineKeyboardButton("👁 Buyurtmani ko'rish", url=post_url)]]
    await context.bot.send_message(
        chat_id=user_id,
        text="✅ Sizning buyurtmangiz tekshiruvdan muvaffaqiyatli o'tdi va kanalga joylandi!",
        reply_markup=InlineKeyboardMarkup(view_keyboard)
    )

    # Admin xabarini yangilash
    await query.message.edit_caption(
        caption=query.message.caption + "\n\n✅ <b>TASDIQLANDI</b>",
        parse_mode="HTML"
    )
    del pending_orders[order_id]

async def admin_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    order_id = int(query.data.split("_")[-1])
    data = pending_orders.get(order_id)
    if not data:
        await query.message.reply_text("❌ Buyurtma topilmadi.")
        return

    user_id = data["user_id"]
    await context.bot.send_message(
        chat_id=user_id,
        text=(
            "❌ Sizning buyurtmangiz adminlar tomonidan bekor qilindi.\n\n"
            "Shikoyatlarni <b>Admin bilan bog'lanish</b> tugmasi orqali yo'llashingiz mumkin."
        ),
        parse_mode="HTML",
        reply_markup=main_menu_keyboard()
    )

    await query.message.edit_caption(
        caption=query.message.caption + "\n\n❌ <b>BEKOR QILINDI</b>",
        parse_mode="HTML"
    )
    del pending_orders[order_id]

# ===================== AKKAUNTLARIM =====================
async def my_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    orders = user_data_store.get(user.id, {}).get("orders", [])

    if not orders:
        await update.message.reply_text("📦 Sizda hech qanday tasdiqlangan akkaunt yo'q.")
        return

    for item in orders:
        data = item["data"]
        caption = build_channel_caption(data)
        keyboard = [[InlineKeyboardButton("🗑 O'chirish", callback_data=f"delete_{item['order_id']}")]]
        await context.bot.send_photo(
            chat_id=user.id,
            photo=data["photo"],
            caption=caption,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def delete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    order_id = int(query.data.split("_")[-1])
    orders = user_data_store.get(user.id, {}).get("orders", [])
    item = next((o for o in orders if o["order_id"] == order_id), None)

    if item:
        # Kanaldan o'chirish
        try:
            await context.bot.delete_message(chat_id=CHANNEL_ID, message_id=item["channel_msg_id"])
        except:
            pass
        user_data_store[user.id]["orders"] = [o for o in orders if o["order_id"] != order_id]
        await query.message.edit_caption(
            caption="🗑 Bu akkaunt o'chirildi.",
            parse_mode="HTML"
        )
    else:
        await query.answer("❌ Topilmadi.", show_alert=True)

# ===================== ADMIN BILAN BOG'LANISH =====================
async def contact_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("👨‍💼 Admin", url=ADMIN_URL)]]
    await update.message.reply_text(
        "📩 Siz adminlarimiz bilan bog'lanishingiz mumkin:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ===================== ASOSIY MENYU HANDLER =====================
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "📦 Akkauntlarim":
        await my_accounts(update, context)
    elif text == "👨‍💼 Admin bilan bog'lanish":
        await contact_admin(update, context)

# ===================== BOT ISHGA TUSHIRISH =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🛒 Buyurtma berish$"), order_start)],
        states={
            CHOOSING_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, choose_type)],
            # Telegram
            TG_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, tg_photo)],
            TG_SUBSCRIBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_subscribers)],
            TG_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_price)],
            TG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_phone)],
            TG_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_username)],
            TG_USER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, tg_user_username)],
            # Instagram
            IG_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, ig_photo)],
            IG_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, ig_link)],
            IG_SUBSCRIBERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ig_subscribers)],
            IG_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ig_price)],
            IG_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ig_phone)],
            IG_USER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ig_user_username)],
            # O'yin
            GAME_PHOTO: [MessageHandler(filters.PHOTO | filters.TEXT, game_photo)],
            GAME_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_price)],
            GAME_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_phone)],
            GAME_USER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, game_user_username)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(check_sub_callback, pattern="^check_sub$"))
    app.add_handler(CallbackQueryHandler(user_confirm_callback, pattern="^user_confirm$"))
    app.add_handler(CallbackQueryHandler(user_cancel_callback, pattern="^user_cancel$"))
    app.add_handler(CallbackQueryHandler(admin_confirm_callback, pattern="^admin_confirm_"))
    app.add_handler(CallbackQueryHandler(admin_cancel_callback, pattern="^admin_cancel_"))
    app.add_handler(CallbackQueryHandler(delete_order_callback, pattern="^delete_"))
    app.add_handler(MessageHandler(
        filters.Regex("^(📦 Akkauntlarim|👨‍💼 Admin bilan bog'lanish)$"),
        main_menu_handler
    ))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
    
