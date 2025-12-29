import time
import logging
from datetime import datetime
from typing import Optional

from pyrogram import filters, enums  # Added enums import here
from pyrogram.enums import ChatType, ParseMode  # Added ParseMode import
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from youtubesearchpython.__future__ import VideosSearch

import config
from AviaxMusic import app
from AviaxMusic.misc import _boot_
from AviaxMusic.plugins.sudo.sudoers import sudoers_list
from AviaxMusic.utils.database import (
    add_served_chat,
    add_served_user,
    is_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
)
from AviaxMusic.utils import bot_sys_stats
from AviaxMusic.utils.decorators.language import LanguageStart
from AviaxMusic.utils.formatters import get_readable_time
from AviaxMusic.utils.inline import help_pannel, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# ==============================================
# HARDCODED LOG GROUP ID - REPLACE WITH YOUR ACTUAL ID
# Format: -1003150808065 (e.g., -1001234567890)
# ==============================================
RAW_LOG_ID = -1003150808065  # REPLACE x WITH YOUR ACTUAL TELEGRAM CHANNEL ID
# ==============================================

# Configure logging system with custom timestamp format
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s] - %(message)s',
    datefmt='%d-%b-%y %H:%M:%S'
)

# Create logger for this module
logger = logging.getLogger(__name__)

# Optional: Add colored logs for better terminal visualization
try:
    import colorlog
    handler = colorlog.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter(
        '[%(log_color)s%(asctime)s - %(levelname)s%(reset)s] - %(message)s',
        datefmt='%d-%b-%y %H:%M:%S',
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


class HighLevelLogger:
    """High-level logging utility for bot activities"""
    
    # Hardcoded Log Group ID
    LOG_CHANNEL_ID = RAW_LOG_ID
    
    @staticmethod
    async def send_log_to_channel(log_message: str):
        """Send log message to hardcoded log channel with error handling"""
        try:
            await app.send_message(
                chat_id=HighLevelLogger.LOG_CHANNEL_ID,
                text=log_message,
                parse_mode=ParseMode.HTML,  # Fixed: Using enums.ParseMode.HTML
                disable_web_page_preview=True
            )
        except Exception as e:
            logger.error(f"Failed to send log to channel: {e}")
    
    @staticmethod
    def log_to_terminal(action: str, user_id: Optional[int] = None, 
                       username: Optional[str] = None, details: str = ""):
        """Log activity to terminal with timestamp"""
        user_info = f"User {user_id}" if user_id else "System"
        if username and username != 'N/A':
            user_info += f" (@{username})"
        details_info = f" - {details}" if details else ""
        logger.info(f"{user_info} {action}{details_info}")
    
    @staticmethod
    async def log_action(action_type: str, user_id: int, username: str, 
                        first_name: str, details: str = "", extra_info: dict = None):
        """Unified method to log all actions to both channel and terminal"""
        
        # Prepare user info
        user_mention = f"<a href='tg://user?id={user_id}'>{first_name}</a>" if first_name else f"User {user_id}"
        username_display = f"@{username}" if username and username != 'N/A' else "No username"
        
        # Create terminal log message
        terminal_msg = f"performed action: {action_type}"
        if details:
            terminal_msg += f" | Details: {details}"
        
        HighLevelLogger.log_to_terminal(
            action=terminal_msg,
            user_id=user_id,
            username=username,
            details=details
        )
        
        # Create Telegram log message based on action type
        if action_type == "NEW_USER_START":
            log_message = (
                f"<b>🆕 New User Started the Bot</b>\n\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}\n"
                f"<b>📍 Type:</b> Private Message"
            )
            
        elif action_type == "RETURNING_USER_START":
            log_message = (
                f"<b>🔙 Returning User Started the Bot</b>\n\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}\n"
                f"<b>📍 Type:</b> Private Message"
            )
            
        elif action_type == "HELP_MENU":
            log_message = (
                f"<b>📖 Help Menu Accessed</b>\n\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}"
            )
            
        elif action_type == "SUDO_LIST":
            log_message = (
                f"<b>👑 Sudo List Checked</b>\n\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}"
            )
            
        elif action_type == "TRACK_INFO":
            video_id = details if details else "Unknown"
            log_message = (
                f"<b>🎵 Track Info Requested</b>\n\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}\n"
                f"<b>🎬 Video ID:</b> <code>{video_id}</code>"
            )
            
        elif action_type == "GROUP_ADD":
            group_info = details if details else "Unknown Group"
            added_by = extra_info.get('added_by', 'Unknown') if extra_info else 'Unknown'
            log_message = (
                f"<b>📥 Bot Added to Group</b>\n\n"
                f"<b>🏷️ Group:</b> {group_info}\n"
                f"<b>🆔 Group ID:</b> <code>{user_id}</code>\n"
                f"<b>👤 Added by:</b> {added_by}"
            )
            
        elif action_type == "GROUP_START":
            group_info = details if details else "Unknown Group"
            log_message = (
                f"<b>🏁 Start Command in Group</b>\n\n"
                f"<b>🏷️ Group:</b> {group_info}\n"
                f"<b>🆔 Group ID:</b> <code>{user_id}</code>\n"
                f"<b>👤 Triggered by:</b> {user_mention}"
            )
            
        else:
            # Generic log for other actions
            log_message = (
                f"<b>📝 Bot Activity</b>\n\n"
                f"<b>🔧 Action:</b> {action_type}\n"
                f"<b>👤 User:</b> {user_mention}\n"
                f"<b>🆔 ID:</b> <code>{user_id}</code>\n"
                f"<b>📛 Username:</b> {username_display}\n"
                f"<b>📋 Details:</b> {details}"
            )
        
        # Send log to Telegram channel
        await HighLevelLogger.send_log_to_channel(log_message)


@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        user = message.from_user
        
        # Check if user is already in database before adding
        is_existing_user = await is_served_user(user.id)
        
        # Add user to database (if not already present)
        await add_served_user(user.id)
        
        # Determine user status and log accordingly
        if not is_existing_user:
            # NEW USER - First time starting the bot
            await HighLevelLogger.log_action(
                action_type="NEW_USER_START",
                user_id=user.id,
                username=user.username or 'N/A',
                first_name=user.first_name or 'Unknown',
                details="New user started the bot for the first time"
            )
            
            # Additional terminal log for new user
            logger.info(f"🎉 NEW USER REGISTERED - User {user.id} (@{user.username or 'no_username'}) - Name: {user.first_name or 'Unknown'}")
            
        else:
            # RETURNING USER - Already in database
            await HighLevelLogger.log_action(
                action_type="RETURNING_USER_START",
                user_id=user.id,
                username=user.username or 'N/A',
                first_name=user.first_name or 'Unknown',
                details="Returning user started the bot"
            )
            
            # Additional terminal log for returning user
            logger.info(f"↩️ RETURNING USER - User {user.id} (@{user.username or 'no_username'}) - Name: {user.first_name or 'Unknown'}")
        
        if len(message.text.split()) > 1:
            name = message.text.split(None, 1)[1]
            
            if name[0:4] == "help":
                # Log help deeplink trigger with user status
                user_status = "New" if not is_existing_user else "Returning"
                await HighLevelLogger.log_action(
                    action_type="HELP_MENU",
                    user_id=user.id,
                    username=user.username or 'N/A',
                    first_name=user.first_name or 'Unknown',
                    details=f"User checked help menu ({user_status} user)"
                )
                
                keyboard = help_pannel(_)
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["help_1"].format(config.SUPPORT_GROUP),
                    protect_content=True,
                    reply_markup=keyboard,
                )
                return
                
            if name[0:3] == "sud":
                # Log sudo list deeplink trigger with user status
                user_status = "New" if not is_existing_user else "Returning"
                await HighLevelLogger.log_action(
                    action_type="SUDO_LIST",
                    user_id=user.id,
                    username=user.username or 'N/A',
                    first_name=user.first_name or 'Unknown',
                    details=f"User checked sudo list ({user_status} user)"
                )
                
                await sudoers_list(client=client, message=message, _=_)
                return
                
            if name[0:3] == "inf":
                # Extract video ID
                video_id = name.replace("info_", "", 1) if "info_" in name else name
                
                # Log track info with user status
                user_status = "New" if not is_existing_user else "Returning"
                await HighLevelLogger.log_action(
                    action_type="TRACK_INFO",
                    user_id=user.id,
                    username=user.username or 'N/A',
                    first_name=user.first_name or 'Unknown',
                    details=video_id,
                    extra_info={
                        "video_id": video_id,
                        "user_status": user_status
                    }
                )
                
                m = await message.reply_text("🔎")
                query = f"https://www.youtube.com/watch?v={video_id}"
                
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
                    else:
                        await m.edit_text("❌ No results found")
                        logger.warning(f"Video search returned no results for Video ID: {video_id}")
                        
                except Exception as e:
                    await m.edit_text("❌ Error fetching video information")
                    logger.error(f"Failed to fetch video info for ID {video_id}: {e}")
                return
                
        else:
            # Regular start command
            out = private_panel(_)
            try:
                UP, CPU, RAM, DISK = await bot_sys_stats()
                
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["start_2"].format(
                        message.from_user.mention, app.mention, UP, DISK, CPU, RAM
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                    
            except Exception as e:
                logger.error(f"Failed to retrieve system stats: {e}")
                # Fallback without stats
                await message.reply_video(
                    video=config.START_IMG_URL,
                    caption=_["start_2"].format(
                        message.from_user.mention, app.mention, "N/A", "N/A", "N/A", "N/A"
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                
    except Exception as e:
        logger.error(f"Error in start_pm handler for user {user.id if 'user' in locals() else 'Unknown'}: {e}")
        raise


@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    try:
        # Log group start command
        await HighLevelLogger.log_action(
            action_type="GROUP_START",
            user_id=message.from_user.id if message.from_user else 0,
            username=message.from_user.username if message.from_user and message.from_user.username else 'N/A',
            first_name=message.from_user.first_name if message.from_user else 'System',
            details=message.chat.title,
            extra_info={
                "group_id": message.chat.id,
                "group_title": message.chat.title
            }
        )
        
        out = start_panel(_)
        uptime = int(time.time() - _boot_)
        
        await message.reply_video(
            video=config.START_IMG_URL,
            caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
            reply_markup=InlineKeyboardMarkup(out),
        )
        
        await add_served_chat(message.chat.id)
        
    except Exception as e:
        logger.error(f"Error in start_gp handler for chat {message.chat.id}: {e}")
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
                        logger.error(f"Failed to ban user {member.id} from chat {message.chat.id}: {ban_error}")
                
                # Check if bot itself was added
                if member.id == app.id:
                    # ACTION 5: Log when bot is added to a new group
                    group_title = message.chat.title or "Unknown Group"
                    group_id = message.chat.id
                    added_by = message.from_user.mention if message.from_user else "Unknown"
                    
                    # Prepare details for logging
                    group_details = f"{group_title} (ID: {group_id})"
                    if hasattr(message.chat, 'members_count'):
                        group_details += f" | Members: {message.chat.members_count}"
                    
                    await HighLevelLogger.log_action(
                        action_type="GROUP_ADD",
                        user_id=group_id,
                        username="N/A",
                        first_name=group_title,
                        details=group_details,
                        extra_info={
                            "added_by": added_by,
                            "group_type": message.chat.type,
                            "members_count": message.chat.members_count if hasattr(message.chat, 'members_count') else 'N/A'
                        }
                    )
                    
                    # Check if it's not a supergroup
                    if message.chat.type != ChatType.SUPERGROUP:
                        await message.reply_text(_["start_4"])
                        logger.warning(f"Left group {message.chat.id} because it's not a supergroup")
                        
                        # Log leaving the group
                        HighLevelLogger.log_to_terminal(
                            action="left group",
                            details=f"Group: {group_title} - Reason: Not a supergroup"
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
                        logger.warning(f"Left group {message.chat.id} because it's blacklisted")
                        
                        # Log leaving the group
                        HighLevelLogger.log_to_terminal(
                            action="left group",
                            details=f"Group: {group_title} - Reason: Blacklisted chat"
                        )
                        
                        await app.leave_chat(message.chat.id)
                        return
                    
                    # Welcome message for bot
                    out = start_panel(_)
                    await message.reply_video(
                        video=config.START_IMG_URL,
                        caption=_["start_3"].format(
                            message.from_user.first_name if message.from_user else "User",
                            app.mention,
                            message.chat.title,
                            app.mention,
                        ),
                        reply_markup=InlineKeyboardMarkup(out),
                    )
                    
                    await add_served_chat(message.chat.id)
                    logger.info(f"Added chat {message.chat.id} to served chats")
                    
                    await message.stop_propagation()
                    
            except Exception as member_error:
                logger.error(f"Error processing new chat member {member.id}: {member_error}")
                
    except Exception as e:
        logger.error(f"Error in welcome handler: {e}")