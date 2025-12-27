from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Ek helper function taaki baar-baar CLOSE button na likhna pade
def close_btn(_):
    return InlineKeyboardButton(text=f"🗑️ {_['CLOSE_BUTTON']}", callback_data="close")

def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    buttons = []
    
    # 1. Timer Button (Agar duration pata hai)
    if DURATION != "Unknown":
        buttons.append([
            InlineKeyboardButton(
                text=f"⏳ {_['QU_B_2'].format(played, dur)}",
                callback_data="GetTimer"
            )
        ])
    
    # 2. Control Buttons (Queued List aur Close ko ek hi line mein rakha hai space bachane ke liye)
    buttons.append([
        InlineKeyboardButton(
            text=f"📜 {_['QU_B_1']}",
            callback_data=f"GetQueued {CPLAY}|{videoid}"
        ),
        close_btn(_)
    ])
    
    return InlineKeyboardMarkup(buttons)

def queue_back_markup(_, CPLAY):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                text=f"🔙 {_['BACK_BUTTON']}",
                callback_data=f"queue_back_timer {CPLAY}"
            ),
            close_btn(_)
        ]
    ])

def aq_markup(_, chat_id):
    # Fix: Isko InlineKeyboardMarkup mein wrap kiya gaya hai
    return InlineKeyboardMarkup([[close_btn(_)]])
