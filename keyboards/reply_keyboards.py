from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_reply_keyboard(is_owner: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="⚔️ Arena (1v1)"), KeyboardButton(text="🗺 Zindon & Reydlar")],
        [KeyboardButton(text="🏰 12 Qirollik"), KeyboardButton(text="🧭 Sahro & Sarguzasht")],
        [KeyboardButton(text="🎒 Inventar"), KeyboardButton(text="🔨 Temirchi & Runalar")],
        [KeyboardButton(text="🛒 Jonli Bozor (P2P)"), KeyboardButton(text="📜 Kvestlar & Yutuqlar")],
        [KeyboardButton(text="⛏ Shaxta & Alximiya"), KeyboardButton(text="🐫 Karvon Savdosi")],
        [KeyboardButton(text="🏰 Gildiya & Qal'alar"), KeyboardButton(text="👑 Oliy Taxt")],
        [KeyboardButton(text="🍻 Taverna"), KeyboardButton(text="📖 Ensiklopediya (Lore)")],
        [KeyboardButton(text="🎁 Kundalik Sovg'a"), KeyboardButton(text="🏆 Reyting")],
        [KeyboardButton(text="👤 Profil & Karta")]
    ]
    if is_owner:
        keyboard.append([KeyboardButton(text="👑 OLIY BOSHQARUV (God-Mode)")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        is_persistent=True
    )
