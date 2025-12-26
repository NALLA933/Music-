from pyrogram.enums import ParseMode
from AviaxMusic import app
from AviaxMusic.utils.database import is_on_off

# Aapka Naya Log Channel ID
NEW_LOG_CHANNEL = -1003150808065

def small_caps(text: str) -> str:
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

async def play_logs(message, streamtype):
    if await is_on_off(2): # Check agar logger database se ON hai
        try:
            chat = message.chat
            user = message.from_user
            
            # Invite link aur member count nikalna
            try:
                invite = await app.export_chat_invite_link(chat.id)
            except:
                invite = "ɴᴏ ɪɴᴠɪᴛᴇ ʟɪɴᴋ"
                
            m_count = await app.get_chat_members_count(chat.id)
            query = message.text.split(None, 1)[1] if len(message.text.split()) > 1 else "ɴ/ᴀ"

            logger_text = small_caps(f"""
✨ NEW STREAM STARTED ✨

👥 GROUP INFO:
├ Name: {chat.title}
├ ID: {chat.id}
├ Link: {invite}
└ Members: {m_count}

👤 USER INFO:
├ Name: {user.mention}
├ ID: {user.id}
└ Username: @{user.username if user.username else 'None'}

🎶 STREAM INFO:
├ Query: {query}
└ Type: {streamtype}
""")
            
            # Message send karna naye ID par
            await app.send_message(
                chat_id=NEW_LOG_CHANNEL,
                text=logger_text,
                disable_web_page_preview=True,
            )
        except Exception as e:
            print(f"ʟᴏɢɢᴇʀ ᴇʀʀᴏʀ: {e}")
            pass
    return
