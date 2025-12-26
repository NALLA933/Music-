from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def stats_buttons(_, status):
    # Agar user Sudo nahi hai
    not_sudo = [
        [
            InlineKeyboardButton(
                text="📊 ᴏᴠᴇʀᴀʟʟ sᴛᴀᴛs",
                callback_data="TopOverall",
            )
        ]
    ]
    
    # Agar user Sudo hai (Dono buttons ek hi line mein better lagte hain)
    sudo = [
        [
            InlineKeyboardButton(
                text="⚙️ ʙᴏᴛ sᴛᴀᴛs",
                callback_data="bot_stats_sudo",
            ),
            InlineKeyboardButton(
                text="📈 ᴏᴠᴇʀᴀʟʟ",
                callback_data="TopOverall",
            ),
        ]
    ]
    
    # Sudo status ke hisab se layout select karna
    base_layout = sudo if status else not_sudo
    
    # Close button hamesha last mein alag row mein
    base_layout.append([
        InlineKeyboardButton(
            text="🗑️ ᴄʟᴏsᴇ",
            callback_data="close",
        )
    ])
    
    return InlineKeyboardMarkup(base_layout)


def back_stats_buttons(_):
    upl = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ ʙᴀᴄᴋ",
                    callback_data="stats_back",
                ),
                InlineKeyboardButton(
                    text="🗑️ ᴄʟᴏsᴇ",
                    callback_data="close",
                ),
            ]
        ]
    )
    return upl
