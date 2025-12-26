from pyrogram.enums import ParseMode
from AviaxMusic import app
from AviaxMusic.utils.database import is_on_off
from config import LOG_GROUP_ID


def small_caps(text: str) -> str:
    """Convert text to small caps"""
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


async def play_logs(message, streamtype, song_name=None, song_link=None, platform="ʏᴏᴜᴛᴜʙᴇ"):
    """Enhanced play logger with detailed information"""
    if await is_on_off(2):
        # Get member count
        try:
            member_count = await app.get_chat_members_count(message.chat.id)
        except:
            member_count = "ɴ/ᴀ"
        
        # Get invite link
        try:
            invite_link = await app.export_chat_invite_link(message.chat.id)
        except:
            invite_link = "ᴘʀɪᴠᴀᴛᴇ"
        
        # Get owner info
        try:
            chat = await app.get_chat(message.chat.id)
            owner_id = chat.owner.id if hasattr(chat, 'owner') and chat.owner else "ɴ/ᴀ"
        except:
            owner_id = "ɴ/ᴀ"
        
        # Get query safely
        try:
            query = message.text.split(None, 1)[1]
        except:
            query = "ɴ/ᴀ"
        
        logger_text = f"""
━━━━━━━━━━━━━━━━━━━━
🎵 <b>ɴᴇᴡ sᴛʀᴇᴀᴍ sᴛᴀʀᴛᴇᴅ</b>
━━━━━━━━━━━━━━━━━━━━

📊 <b>ɢʀᴏᴜᴘ ɪɴғᴏ:</b>
├ <b>ɢʀᴏᴜᴘ ɪᴅ:</b> <code>{message.chat.id}</code>
├ <b>ɢʀᴏᴜᴘ ɴᴀᴍᴇ:</b> {message.chat.title}
├ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.chat.username if message.chat.username else 'ɴᴏɴᴇ'}
├ <b>ᴏᴡɴᴇʀ ɪᴅ:</b> <code>{owner_id}</code>
├ <b>ᴛᴏᴛᴀʟ ᴍᴇᴍʙᴇʀs:</b> {member_count}
└ <b>ɢʀᴏᴜᴘ ʟɪɴᴋ:</b> {invite_link}

👤 <b>ᴜsᴇʀ ɪɴғᴏ:</b>
├ <b>ᴜsᴇʀ ɪᴅ:</b> <code>{message.from_user.id}</code>
├ <b>ɴᴀᴍᴇ:</b> {message.from_user.mention}
└ <b>ᴜsᴇʀɴᴀᴍᴇ:</b> @{message.from_user.username if message.from_user.username else 'ɴᴏɴᴇ'}

🎶 <b>sᴛʀᴇᴀᴍ ɪɴғᴏ:</b>
├ <b>ǫᴜᴇʀʏ:</b> {query}
├ <b>sᴏɴɢ ɴᴀᴍᴇ:</b> {song_name if song_name else query}
├ <b>sᴏɴɢ ʟɪɴᴋ:</b> {song_link if song_link else 'ɴ/ᴀ'}
├ <b>ᴘʟᴀᴛғᴏʀᴍ:</b> {platform}
└ <b>sᴛʀᴇᴀᴍᴛʏᴘᴇ:</b> {streamtype}

━━━━━━━━━━━━━━━━━━━━
"""
        
        if message.chat.id != LOG_GROUP_ID:
            try:
                await app.send_message(
                    chat_id=LOG_GROUP_ID,
                    text=logger_text,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
            except Exception as e:
                print(f"Logger Error: {e}")
        return
Option 2: Dono Functions Ko Use Karo
Agar tum chahte ho ki inline.py wala function bhi kaam kare, to play.py mein dono call karo:
from AviaxMusic.utils.inline import log_stream_info
from AviaxMusic.logging import play_logs

# Inside your play handler
await play_logs(message, streamtype="ᴠɪᴅᴇᴏ")  # Existing logger

# AND also call your new logger
await log_stream_info(
    client=app,
    chat_id=message.chat.id,
    user_id=message.from_user.id,
    username=message.from_user.username,
    song_name="Song Title",
    song_link="https://youtube.com/...",
    platform="ʏᴏᴜᴛᴜʙᴇ" )