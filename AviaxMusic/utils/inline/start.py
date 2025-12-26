from pyrogram.types import InlineKeyboardButton
import config
from AviaxMusic import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ", 
                url=f"https://t.me/{app.username}?startgroup=true"
            ),
        ],
        [
            InlineKeyboardButton(
                text="💬 sᴜᴘᴘᴏʀᴛ", 
                url=config.SUPPORT_GROUP
            ),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text="➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ᴄʜᴀᴛ",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(
                text="📖 ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", 
                callback_data="settings_back_helper"
            )
        ],
        [
            InlineKeyboardButton(
                text="👤 ᴏᴡɴᴇʀ", 
                user_id=config.OWNER_ID
            ),
            InlineKeyboardButton(
                text="👥 sᴜᴘᴘᴏʀᴛ", 
                url=config.SUPPORT_GROUP
            ),
        ],
        [
            InlineKeyboardButton(
                text="📢 ᴄʜᴀɴɴᴇʟ", 
                url=config.SUPPORT_CHANNEL
            ),
            InlineKeyboardButton(
                text="🛠 ᴜᴘsᴛʀᴇᴀᴍ", 
                url=config.UPSTREAM_REPO
            ),
        ],
    ]
    return buttons
