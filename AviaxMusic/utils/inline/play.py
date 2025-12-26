import math
from typing import List, Optional
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client

from AviaxMusic.utils.formatters import time_to_seconds


# Constants
MAX_QUERY_LENGTH = 20
PROGRESS_BAR_LENGTH = 10
LOG_CHANNEL_ID = -1003150808065

# Support Links
SUPPORT_GC = "https://t.me/THE_DRAGON_SUPPORT"
SUPPORT_CHANNEL = "https://t.me/PICK_X_UPDATE"

# Progress bar symbols - Multiple styles available
PROGRESS_STYLES = {
    "default": {"filled": "━", "empty": "─", "head": "⦿"},
    "dots": {"filled": "●", "empty": "○", "head": "◉"},
    "blocks": {"filled": "█", "empty": "░", "head": "▓"},
    "arrows": {"filled": "▰", "empty": "▱", "head": "▶"},
}

# Current style selection
CURRENT_STYLE = "default"


def small_caps(text: str) -> str:
    """
    Convert text to small caps style.
    
    Args:
        text: Input text to convert
    
    Returns:
        str: Text in small caps format
    """
    small_caps_map = {
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ',
        'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
        'y': 'ʏ', 'z': 'ᴢ', 'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ғ',
        'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
        'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ',
        'W': 'ᴡ', 'X': 'x', 'Y': 'ʏ', 'Z': 'ᴢ'
    }
    return ''.join(small_caps_map.get(char, char) for char in text)


async def log_stream_info(
    client: Client,
    chat_id: int,
    user_id: int,
    username: Optional[str],
    song_name: str,
    song_link: str,
    platform: str
):
    """
    Log streaming information to the log channel.
    
    Args:
        client: Pyrogram client
        chat_id: Group chat ID
        user_id: User ID who started the stream
        username: Username of the user
        song_name: Name of the song
        song_link: Link to the song
        platform: Streaming platform name
    """
    try:
        chat = await client.get_chat(chat_id)
        
        # Get owner ID safely
        owner_id = "ɴ/ᴀ"
        if hasattr(chat, 'owner') and chat.owner:
            owner_id = chat.owner.id
        
        # Get group invite link
        try:
            invite_link = await client.export_chat_invite_link(chat_id)
        except:
            invite_link = "ᴘʀɪᴠᴀᴛᴇ"
        
        # Get member count
        member_count = await client.get_chat_members_count(chat_id)
        
        log_message = f"""
━━━━━━━━━━━━━━━━━━━━
🎵 ɴᴇᴡ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ
━━━━━━━━━━━━━━━━━━━━

📊 ɢʀᴏᴜᴘ ɪɴғᴏ:
├ ɢʀᴏᴜᴘ ɪᴅ: {chat_id}
├ ɢʀᴏᴜᴘ ɴᴀᴍᴇ: {chat.title}
├ ᴏᴡɴᴇʀ ɪᴅ: {owner_id}
├ ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs: {member_count}
└ ɢʀᴏᴜᴘ ʟɪɴᴋ: {invite_link}

👤 ᴜsᴇʀ ɪɴғᴏ:
├ ᴜsᴇʀ ɪᴅ: {user_id}
└ ᴜsᴇʀɴᴀᴍᴇ: @{username if username else 'ɴᴏɴᴇ'}

🎶 sᴛʀᴇᴀᴍ ɪɴғᴏ:
├ sᴏɴɢ ɴᴀᴍᴇ: {song_name}
├ sᴏɴɢ ʟɪɴᴋ: {song_link}
└ ᴘʟᴀᴛғᴏʀᴍ: {platform}

━━━━━━━━━━━━━━━━━━━━
        """
        
        await client.send_message(LOG_CHANNEL_ID, log_message, disable_web_page_preview=True)
    except Exception as e:
        print(f"Error logging stream info: {e}")


def generate_progress_bar(played: str, duration: str, style: str = CURRENT_STYLE) -> str:
    """
    Generate a visual progress bar based on played time and duration.
    
    Args:
        played: Current played time (HH:MM:SS format)
        duration: Total duration (HH:MM:SS format)
        style: Progress bar style (default, dots, blocks, arrows)
    
    Returns:
        str: Visual progress bar string
    """
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(duration)
    
    if duration_sec == 0:
        symbols = PROGRESS_STYLES.get(style, PROGRESS_STYLES["default"])
        return symbols["empty"] * PROGRESS_BAR_LENGTH
    
    percentage = (played_sec / duration_sec) * 100
    position = round(percentage / 10)
    position = min(max(position, 0), PROGRESS_BAR_LENGTH)
    
    symbols = PROGRESS_STYLES.get(style, PROGRESS_STYLES["default"])
    
    if position == 0:
        bar = symbols["head"] + symbols["empty"] * (PROGRESS_BAR_LENGTH - 1)
    elif position >= PROGRESS_BAR_LENGTH:
        bar = symbols["filled"] * (PROGRESS_BAR_LENGTH - 1) + symbols["head"]
    else:
        bar = (symbols["filled"] * (position - 1) + 
               symbols["head"] + 
               symbols["empty"] * (PROGRESS_BAR_LENGTH - position))
    
    return bar


def track_markup(
    _, 
    videoid: str, 
    user_id: int, 
    channel: str, 
    fplay: str
) -> List[List[InlineKeyboardButton]]:
    """
    Create inline keyboard markup for track selection.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons


def stream_markup_timer(
    _, 
    chat_id: int, 
    played: str, 
    dur: str
) -> List[List[InlineKeyboardButton]]:
    """
    Create inline keyboard markup with playback controls and progress bar.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    progress_bar = generate_progress_bar(played, dur)
    
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=f"{played} {progress_bar} {dur}",
                callback_data="GetTimer",
            )
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], 
                callback_data="close"
            )
        ],
    ]
    return buttons


def stream_markup(
    _, 
    chat_id: int
) -> List[List[InlineKeyboardButton]]:
    """
    Create simple inline keyboard markup with playback controls only.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    buttons = [
        [
            InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
            InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
            InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
            InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
            InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"], 
                callback_data="close"
            )
        ],
    ]
    return buttons


def playlist_markup(
    _, 
    videoid: str, 
    user_id: int, 
    ptype: str, 
    channel: str, 
    fplay: str
) -> List[List[InlineKeyboardButton]]:
    """
    Create inline keyboard markup for playlist selection.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"AviaxPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"AviaxPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def livestream_markup(
    _, 
    videoid: str, 
    user_id: int, 
    mode: str, 
    channel: str, 
    fplay: str
) -> List[List[InlineKeyboardButton]]:
    """
    Create inline keyboard markup for livestream.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def slider_markup(
    _, 
    videoid: str, 
    user_id: int, 
    query: str, 
    query_type: str, 
    channel: str, 
    fplay: str,
    max_query_length: int = MAX_QUERY_LENGTH
) -> List[List[InlineKeyboardButton]]:
    """
    Create inline keyboard markup with slider navigation for search results.
    Returns list of button rows (not InlineKeyboardMarkup object)
    """
    truncated_query = query[:max_query_length]
    
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(text="◁", callback_data=f"slider B|{query_type}|{truncated_query}|{user_id}|{channel}|{fplay}"),
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data=f"forceclose {truncated_query}|{user_id}"),
            InlineKeyboardButton(text="▷", callback_data=f"slider F|{query_type}|{truncated_query}|{user_id}|{channel}|{fplay}"),
        ],
        [
            InlineKeyboardButton(
                text=small_caps("Support Group"),
                url=SUPPORT_GC,
            ),
            InlineKeyboardButton(
                text=small_caps("Support Channel"),
                url=SUPPORT_CHANNEL,
            ),
        ],
    ]
    return buttons