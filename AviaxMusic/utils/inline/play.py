import math
from typing import List, Optional
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram import Client
from pyrogram.types import Message

from AviaxMusic.utils.formatters import time_to_seconds


# Constants
MAX_QUERY_LENGTH = 20
PROGRESS_BAR_LENGTH = 10
SUPPORT_CHAT_LINK = "https://t.me/THE_DRAGON_SUPPORT"
LOG_CHANNEL_ID = -1003150808065

# Progress bar symbols - Multiple styles available
PROGRESS_STYLES = {
    "default": {"filled": "━", "empty": "─", "head": "◉"},
    "dots": {"filled": "●", "empty": "○", "head": "◉"},
    "blocks": {"filled": "█", "empty": "░", "head": "▓"},
    "arrows": {"filled": "▰", "empty": "▱", "head": "▶"},
}

# Current style selection
CURRENT_STYLE = "default"


async def send_play_log(
    client: Client,
    message: Message,
    song_name: str,
    song_link: str,
    platform: str
) -> None:
    """
    Send detailed play log to the log channel.
    
    Args:
        client: Pyrogram client
        message: Message object
        song_name: Name of the song
        song_link: Link to the song
        platform: Streaming platform name (YouTube, Spotify, etc.)
    """
    try:
        chat = message.chat
        user = message.from_user
        
        # Get group link
        try:
            if chat.username:
                group_link = f"https://t.me/{chat.username}"
            else:
                invite_link = await client.export_chat_invite_link(chat.id)
                group_link = invite_link
        except:
            group_link = "Private Group"
        
        # Get owner info
        try:
            chat_full = await client.get_chat(chat.id)
            owner_id = "N/A"
            async for member in client.get_chat_members(chat.id, filter="administrators"):
                if member.status == "creator":
                    owner_id = member.user.id
                    break
        except:
            owner_id = "N/A"
        
        # Get total members
        try:
            members_count = await client.get_chat_members_count(chat.id)
        except:
            members_count = "N/A"
        
        # Create log message
        log_message = f"""
╭━━━━━━━━━━━━━━━━━━━╮
┃  🎵 **NEW SONG PLAYED** 🎵
╰━━━━━━━━━━━━━━━━━━━╯

📊 **Group Information:**
├ **Group ID:** `{chat.id}`
├ **Group Name:** {chat.title}
├ **Group Link:** {group_link}
├ **Owner ID:** `{owner_id}`
└ **Total Members:** {members_count}

👤 **Player Information:**
├ **User ID:** `{user.id}`
├ **Username:** @{user.username if user.username else 'No Username'}
├ **Name:** {user.first_name} {user.last_name if user.last_name else ''}
└ **User Link:** [Profile](tg://user?id={user.id})

🎶 **Song Details:**
├ **Song Name:** {song_name}
├ **Platform:** {platform}
└ **Song Link:** {song_link}

⏰ **Time:** {message.date.strftime('%Y-%m-%d %H:%M:%S')}
━━━━━━━━━━━━━━━━━━━━━
"""
        
        await client.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=log_message,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        print(f"Error sending log: {e}")


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
    
    Args:
        _: Language dictionary
        videoid: Video/Track ID
        user_id: User ID who requested
        channel: Channel identifier
        fplay: Force play flag
    
    Returns:
        List of button rows
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
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
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
    
    Args:
        _: Language dictionary
        chat_id: Chat ID where music is playing
        played: Current played time
        dur: Total duration
    
    Returns:
        List of button rows with controls and progress bar
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
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
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
    
    Args:
        _: Language dictionary
        chat_id: Chat ID where music is playing
    
    Returns:
        List of button rows with controls
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
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
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
    
    Args:
        _: Language dictionary
        videoid: Video/Track ID
        user_id: User ID who requested
        ptype: Playlist type
        channel: Channel identifier
        fplay: Force play flag
    
    Returns:
        List of button rows
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
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
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
    
    Args:
        _: Language dictionary
        videoid: Video/Stream ID
        user_id: User ID who requested
        mode: Stream mode
        channel: Channel identifier
        fplay: Force play flag
    
    Returns:
        List of button rows
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
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
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
    
    Args:
        _: Language dictionary
        videoid: Video/Track ID
        user_id: User ID who requested
        query: Search query
        query_type: Type of query
        channel: Channel identifier
        fplay: Force play flag
        max_query_length: Maximum length for query display
    
    Returns:
        List of button rows with navigation controls
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
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{truncated_query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text="💬 Support",
                url=SUPPORT_CHAT_LINK,
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{truncated_query}|{user_id}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {truncated_query}|{user_id}",
            ),
        ],
    ]
    return buttons