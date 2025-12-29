import time
import logging
from datetime import datetime
from typing import Optional

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.plugins.sudo.sudoers import sudoers_list
from AviaxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from AviaxMusic.utils import bot_sys_stats
from AviaxMusic.utils.decorators.language import LanguageStart
from AviaxMusic.utils.formatters import get_readable_time
from AviaxMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# Configure logging system
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Optional: Add colored logs for better terminal visualization
try:
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    ))
    logger.handlers = [handler]
except ImportError:
    # colorlog not installed, use default logging
    pass


class BotLogger:
    """Centralized logging utility for the bot"""
    
    @staticmethod
    def log_user_start(user_id: int, username: Optional[str], 
                      first_name: Optional[str], deeplink: Optional[str] = None):
        """Log when a user starts the bot"""
        user_info = f"User {user_id} ({first_name or 'Unknown'}"
        if username:
            user_info += f", @{username}"
        user_info += ")"
        
        if deeplink:
            logger.info(f"{user_info} started bot with deeplink: {deeplink}")
        else:
            logger.info(f"{user_info} started the bot")
    
    @staticmethod
    def log_group_join(chat_id: int, chat_title: str, members_count: int = None):
        """Log when bot is added to a group"""
        members_info = f" ({members_count} members)" if members_count else ""
        logger.info(f"Bot added to group: '{chat_title}' (ID: {chat_id}){members_info}")
    
    @staticmethod
    def log_group_leave(chat_id: int, chat_title: str, reason: str):
        """Log when bot leaves a group"""
        logger.warning(f"Bot left group '{chat_title}' (ID: {chat_id}) - Reason: {reason}")
    
    @staticmethod
    def log_deeplink_trigger(user_id: int, deeplink_type: str, details: str = ""):
        """Log when a user triggers a specific deep-link"""
        details_text = f" - {details}" if details else ""
        logger.info(f"User {user_id} triggered {deeplink_type} deeplink{details_text}")
    
    @staticmethod
    def log_error(error_msg: str, exception: Exception = None, context: dict = None):
        """Log errors with context"""
        context_info = f" | Context: {context}" if context else ""
        if exception:
            logger.error(f"{error_msg}{context_info}", exc_info=exception)
        else:
            logger.error(f"{error_msg}{context_info}")
    
    @staticmethod
    def log_system_event(event: str, details: str = ""):
        """Log system-level events"""
        details_text = f": {details}" if details else ""
        logger.info(f"System Event - {event}{details_text}")


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        user = message.from_user
        await add_served_user(user.id)
        
        # Log user start
        BotLogger.log_user_start(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        
        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]
            
            if name[0:4] == "help":
                # Log help deeplink trigger
                BotLogger.log_deeplink_trigger(
                    user_id=user.id,
                    deeplink_type="help"
                )
                
                keyboard = help_pannel(_)
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["help_1"].format(config.SUPPORT_GROUP),
                    protect_content=True,
                    reply_markup=keyboard,
                )
                
                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOG_GROUP_ID,
                        text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ʜᴇʟᴘ ᴍᴇɴᴜ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                    )
                return
                
            if name[0:3] == "sud":
                # Log sudo list deeplink trigger
                BotLogger.log_deeplink_trigger(
                    user_id=user.id,
                    deeplink_type="sudo_list"
                )
                
                await sudoers_list(client=client, message=message, _=_)
                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOG_GROUP_ID,
                        text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                    )
                return
                
            if name[0:3] == "inf":
                # Log info deeplink trigger
                BotLogger.log_deeplink_trigger(
                    user_id=user.id,
                    deeplink_type="track_info",
                    details=f"query: {name}"
                )
                
                m = await message.reply_text("🔎")
                query = (str(name)).replace("info_", "", 1)
                query = f"https://www.youtube.com/watch?v={query}"
                
                try:
                    results = VideosSearch(query, limit=1)
                    video_data = await results.next()
                    
                    if "result" in video_data and video_data["result"]:
                        result = video_data["result"][0]
                        title = result["title"]
                        duration = result["duration"]
                        views = result["viewCount"]["short"]
                        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                        channellink = result["channel"]["link"]
                        channel = result["channel"]["name"]
                        link = result["link"]
                        published = result["publishedTime"]
                        
                        searched_text = _["start_6"].format(
                            title, duration, views, published, channellink, channel, app.mention
                        )
                        
                        key = InlineKeyboardMarkup([
                            [
                                InlineKeyboardButton(text=_["S_B_8"], url=link),
                                InlineKeyboardButton(text=_["S_B_9"], url=config.SUPPORT_GROUP),
                            ],
                        ])
                        
                        await m.delete()
                        await app.send_photo(
                            chat_id=message.chat.id,
                            photo=thumbnail,
                            caption=searched_text,
                            reply_markup=key,
                        )
                        
                        if await is_on_off(2):
                            await app.send_message(
                                chat_id=config.LOG_GROUP_ID,
                                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                            )
                    else:
                        await m.edit_text("❌ No results found")
                        logger.warning(f"Video search returned no results for query: {query}")
                        
                except Exception as e:
                    await m.edit_text("❌ Error fetching video information")
                    BotLogger.log_error(
                        error_msg="Failed to fetch video information",
                        exception=e,
                        context={"user_id": user.id, "query": query}
                    )
                return
                
        else:
            # Regular start command
            BotLogger.log_user_start(
                user_id=user.id,
                username=user.username,
                first_name=user.first_name,
                deeplink="main_menu"
            )
            
            out = private_panel(_)
            try:
                UP, CPU, RAM, DISK = await bot_sys_stats()
                stats_info = f"UP: {UP}, CPU: {CPU}, RAM: {RAM}, DISK: {DISK}"
                logger.debug(f"System stats retrieved: {stats_info}")
                
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["start_2"].format(
                        message.from_user.mention, app.mention, UP, DISK, CPU, RAM
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                
                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOG_GROUP_ID,
                        text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> @{message.from_user.username}",
                    )
                    
            except Exception as e:
                BotLogger.log_error(
                    error_msg="Failed to retrieve system stats",
                    exception=e,
                    context={"user_id": user.id}
                )
                # Fallback without stats
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["start_2"].format(
                        message.from_user.mention, app.mention, "N/A", "N/A", "N/A", "N/A"
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                
    except Exception as e:
        BotLogger.log_error(
            error_msg="Error in start_pm handler",
            exception=e,
            context={"user_id": message.from_user.id if message.from_user else "Unknown"}
        )
        raise


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        # Log group start command
        logger.info(
            f"Start command in group: '{message.chat.title}' (ID: {message.chat.id}) "
            f"by User {message.from_user.id if message.from_user else 'Unknown'}"
        )
        
        out = start_panel(_)
        uptime = int(time.time() - _boot_)
        
        await message.reply_video(
            video=config.START_IMG_URL,
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )
        
        await add_served_chat(message.chat.id)
        BotLogger.log_system_event(
            event="Group served chat added",
            details=f"Chat ID: {message.chat.id}"
        )
        
    except Exception as e:
        BotLogger.log_error(
            error_msg="Error in start_gp handler",
            exception=e,
            context={"chat_id": message.chat.id, "chat_title": message.chat.title}
        )
        raise


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    try:
        for member in message.new_chat_members:
            try:
                language = await get_lang(message.chat.id)
                _ = get_string(language)
                
                # Check if member is banned
                if await is_banned_user(member.id):
                    logger.warning(
                        f"Banned user {member.id} attempted to join "
                        f"chat {message.chat.id}. Banning from chat."
                    )
                    try:
                        await message.chat.ban_member(member.id)
                    except Exception as ban_error:
                        BotLogger.log_error(
                            error_msg="Failed to ban user from chat",
                            exception=ban_error,
                            context={
                                "user_id": member.id,
                                "chat_id": message.chat.id
                            }
                        )
                
                # Check if bot itself was added
                if member.id == app.id:
                    # Log bot being added to group
                    BotLogger.log_group_join(
                        chat_id=message.chat.id,
                        chat_title=message.chat.title,
                        members_count=message.chat.members_count
                    )
                    
                    # Check if it's not a supergroup
                    if message.chat.type != ChatType.SUPERGROUP:
                        await message.reply_text(_["start_4"])
                        BotLogger.log_group_leave(
                            chat_id=message.chat.id,
                            chat_title=message.chat.title,
                            reason="Not a supergroup"
                        )
                        await app.leave_chat(message.chat.id)
                        return
                    
                    # Check if chat is blacklisted
                    if message.chat.id in await blacklisted_chats():
                        await message.reply_text(
                            _["start_5"].format(
                                app.mention,
                                f"https://t.me/{app.username}?start=sudolist",
                                config.SUPPORT_GROUP,
                            ),
                            disable_web_page_preview=True,
                        )
                        BotLogger.log_group_leave(
                            chat_id=message.chat.id,
                            chat_title=message.chat.title,
                            reason="Blacklisted chat"
                        )
                        await app.leave_chat(message.chat.id)
                        return
                    
                    # Welcome message for bot
                    out = start_panel(_)
                    await message.reply_video(
                        video=config.START_IMG_URL,
                        caption=_["start_3"].format(
                            message.from_user.first_name,
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=InlineKeyboardMarkup(out),
                    )
                    
                    await add_served_chat(message.chat.id)
                    BotLogger.log_system_event(
                        event="New group served",
                        details=f"Chat: {message.chat.title} (ID: {message.chat.id})"
                    )
                    
                    await message.stop_propagation()
                    
            except Exception as member_error:
                BotLogger.log_error(
                    error_msg="Error processing new chat member",
                    exception=member_error,
                    context={
                        "member_id": member.id,
                        "chat_id": message.chat.id,
                        "chat_title": message.chat.title
                    }
                )
                
    except Exception as e:
        BotLogger.log_error(
            error_msg="Error in welcome handler",
            exception=e,
            context={"chat_id": message.chat.id if message.chat else "Unknown"}
        )


# Optional: Add performance logging decorator
def log_performance(func):
    """Decorator to log function execution time"""
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            exec_time = time.time() - start_time
            if exec_time > 1.0:  # Log only if execution takes more than 1 second
                logger.warning(
                    f"Performance alert: {func.__name__} took {exec_time:.2f} seconds to execute"
                )
    return wrapper


# Performance monitoring for critical functions (optional)
@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
@log_performance
async def start_pm_perf_wrapped(client, message: Message, _):
    """Wrapped version with performance logging"""
    return await start_pm(client, message, _)