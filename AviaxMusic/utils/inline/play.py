import math
from typing import List
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from AviaxMusic.utils.formatters import time_to_seconds


# Constants
MAX_QUERY_LENGTH = 20
PROGRESS_BAR_LENGTH = 10

# Progress bar symbols - Multiple styles available
PROGRESS_STYLES = {
    "default": {"filled": "━", "empty": "─", "head": "◉"},
    "dots": {"filled": "●", "empty": "○", "head": "◉"},
    "blocks": {"filled": "█", "empty": "░", "head": "▓"},
    "arrows": {"filled": "▰", "empty": "▱", "head": "▶"},
}

# Current style selection
CURRENT_STYLE = "default"


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
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {truncated_query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{truncated_query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons