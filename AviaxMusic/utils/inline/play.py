import math
from pyrogram.types import InlineKeyboardButton
from AviaxMusic.utils.formatters import time_to_seconds

def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text="ᴀᴜᴅɪᴏ ⊚",
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="ᴠɪᴅᴇᴏ ◈",
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="ᴄʟᴏsᴇ ⊗",
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    
    # Modern Solid Progress Bar Style
    if 0 < umm <= 10:
        bar = "●━━━━━━━━━"
    elif 10 < umm < 20:
        bar = "━●━━━━━━━━"
    elif 20 <= umm < 30:
        bar = "━━●━━━━━━━"
    elif 30 <= umm < 40:
        bar = "━━━●━━━━━━"
    elif 40 <= umm < 50:
        bar = "━━━━●━━━━━"
    elif 50 <= umm < 60:
        bar = "━━━━━●━━━━"
    elif 60 <= umm < 70:
        bar = "━━━━━━●━━━"
    elif 70 <= umm < 80:
        bar = "━━━━━━━●━━"
    elif 80 <= umm < 95:
        bar = "━━━━━━━━●━"
    else:
        bar = "━━━━━━━━━●"
        
    buttons = [
        [
            InlineKeyboardButton(text="⊳", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="Ⅱ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="↠", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(text="ᴠᴏʟ −", callback_data=f"ADMIN VolDown|{chat_id}"),
            InlineKeyboardButton(text="ᴠᴏʟ +", callback_data=f"ADMIN VolUp|{chat_id}"),
        ],
        [InlineKeyboardButton(text="ᴄʟᴏsᴇ ⊗", callback_data="close")],
    ]
    return buttons

def stream_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="⊳", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="Ⅱ", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="↠", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [InlineKeyboardButton(text="ᴄʟᴏsᴇ ⊗", callback_data="close")],
    ]
    return buttons
