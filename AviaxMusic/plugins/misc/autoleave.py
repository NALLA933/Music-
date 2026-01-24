"""
Production-Ready Autoleave Module
Enhanced with performance, safety, and multi-group management
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Set, List
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.errors import (
    FloodWait, UserNotParticipant, ChannelInvalid,
    ChatAdminRequired, PeerIdInvalid
)

from config import LOG_GROUP_ID, ALLOWED_CHATS
from AviaxMusic.core.call import Aviax
from AviaxMusic.utils.database import db_manager

logger = logging.getLogger(__name__)


class AutoLeaveManager:
    """
    Enhanced AutoLeave Manager with:
    - Smart chat filtering
    - Rate limiting
    - Performance monitoring
    - Safe cleanup
    """
    
    def __init__(self):
        self.running = False
        self.stats = {
            "total_left": 0,
            "errors": 0,
            "last_run": None,
            "skipped_chats": 0
        }
        
        # Whitelist of chats that should never be left
        self.whitelist_chats: Set[int] = set()
        
        # Chats with active voice sessions
        self.active_voice_chats: Set[int] = set()
        
        # Recently left chats (prevent rejoining loop)
        self.recently_left: Dict[int, datetime] = {}
        
        # Monitoring
        self.monitoring_task = None
        self.cleanup_interval = 900  # 15 minutes
        self.max_leaves_per_cycle = 20
        self.min_chat_age = timedelta(hours=24)  # Don't leave new chats
    
    async def initialize(self):
        """Initialize the autoleave manager"""
        try:
            # Load whitelist from config
            self.whitelist_chats = set(getattr(config, 'WHITELIST_CHATS', []))
            
            # Add LOG_GROUP_ID to whitelist
            if LOG_GROUP_ID:
                self.whitelist_chats.add(LOG_GROUP_ID)
            
            # Add allowed chats from config
            if hasattr(config, 'ALLOWED_CHATS'):
                for chat_id in config.ALLOWED_CHATS:
                    self.whitelist_chats.add(chat_id)
            
            # Add any other essential chats
            essential_chats = [
                -1002016928980, -1002200386150, -1001397779415
            ]
            self.whitelist_chats.update(essential_chats)
            
            logger.info(f"✅ AutoLeave initialized. Whitelist: {len(self.whitelist_chats)} chats")
            return True
            
        except Exception as e:
            logger.error(f"❌ AutoLeave initialization failed: {e}")
            return False
    
    async def start_monitoring(self):
        """Start periodic autoleave monitoring"""
        if self.running:
            logger.warning("AutoLeave monitoring already running")
            return
        
        self.running = True
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("🚀 AutoLeave monitoring started")
    
    async def stop_monitoring(self):
        """Stop autoleave monitoring"""
        if not self.running:
            return
        
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("🛑 AutoLeave monitoring stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                await asyncio.sleep(self.cleanup_interval)
                
                # Skip if not enabled
                if not await self._is_autoleave_enabled():
                    continue
                
                # Update active voice chats
                await self._update_active_voice_chats()
                
                # Perform cleanup for each assistant
                await self._perform_cleanup_cycle()
                
                # Cleanup recently left cache
                await self._cleanup_recently_left()
                
                self.stats["last_run"] = datetime.now()
                
                # Log stats periodically
                if self.stats["total_left"] % 100 == 0:
                    logger.info(f"📊 AutoLeave Stats: {self.stats}")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _update_active_voice_chats(self):
        """Update list of chats with active voice sessions"""
        try:
            # Get active chats from VoiceChatManager
            self.active_voice_chats = set(Aviax.active_chats.keys())
            
            # Also check database for active chats
            async with db_manager.get_session() as db:
                cursor = db.active_chats.find({"active": True})
                async for doc in cursor:
                    self.active_voice_chats.add(doc["chat_id"])
            
            logger.debug(f"Active voice chats: {len(self.active_voice_chats)}")
            
        except Exception as e:
            logger.error(f"Failed to update active voice chats: {e}")
    
    async def _perform_cleanup_cycle(self):
        """Perform one cleanup cycle"""
        from AviaxMusic.core.userbot import assistants
        
        leaves_in_cycle = 0
        
        for assistant_num in assistants:
            try:
                client = await self._get_assistant_client(assistant_num)
                if not client:
                    continue
                
                # Leave inactive chats for this assistant
                leaves = await self._cleanup_assistant_chats(client)
                leaves_in_cycle += leaves
                
                # Stop if we've reached the limit
                if leaves_in_cycle >= self.max_leaves_per_cycle:
                    logger.info(f"Reached max leaves per cycle ({self.max_leaves_per_cycle})")
                    break
                
                # Small delay between assistants
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Cleanup cycle error for assistant {assistant_num}: {e}")
        
        if leaves_in_cycle > 0:
            logger.info(f"Left {leaves_in_cycle} chats in this cycle")
        
        self.stats["total_left"] += leaves_in_cycle
    
    async def _cleanup_assistant_chats(self, client: Client) -> int:
        """Cleanup inactive chats for a specific assistant"""
        leaves_count = 0
        
        try:
            async for dialog in client.get_dialogs(limit=100):
                try:
                    # Check if we should leave this chat
                    should_leave = await self._should_leave_chat(client, dialog)
                    
                    if should_leave:
                        success = await self._leave_chat_safely(client, dialog.chat.id)
                        if success:
                            leaves_count += 1
                            # Record when we left
                            self.recently_left[dialog.chat.id] = datetime.now()
                            
                        # Check limit
                        if leaves_count >= 5:  # Max 5 per assistant per cycle
                            break
                            
                except Exception as e:
                    logger.error(f"Error processing chat {dialog.chat.id}: {e}")
                    continue
            
            return leaves_count
            
        except Exception as e:
            logger.error(f"Error getting dialogs: {e}")
            return 0
    
    async def _should_leave_chat(self, client: Client, dialog) -> bool:
        """Determine if we should leave a chat"""
        chat = dialog.chat
        
        # Skip if not a group/supergroup/channel
        if chat.type not in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
            return False
        
        # Skip whitelisted chats
        if chat.id in self.whitelist_chats:
            return False
        
        # Skip if recently left (within 24 hours)
        if chat.id in self.recently_left:
            time_since_left = datetime.now() - self.recently_left[chat.id]
            if time_since_left < timedelta(hours=24):
                return False
        
        # Skip if we have active voice session
        if chat.id in self.active_voice_chats:
            return False
        
        # Check if chat is active in database
        if await self._is_chat_active(chat.id):
            return False
        
        # Check if bot is admin (don't leave if admin)
        if await self._is_bot_admin(client, chat.id):
            return False
        
        # Check if chat has recent activity
        if await self._has_recent_activity(client, chat.id):
            return False
        
        # Check minimum chat age
        if await self._is_new_chat(client, chat.id):
            return False
        
        return True
    
    async def _is_chat_active(self, chat_id: int) -> bool:
        """Check if chat is marked as active in database"""
        try:
            async with db_manager.get_session() as db:
                doc = await db.active_chats.find_one({
                    "chat_id": chat_id,
                    "active": True
                })
                return bool(doc)
        except Exception:
            return False
    
    async def _is_bot_admin(self, client: Client, chat_id: int) -> bool:
        """Check if bot is admin in the chat"""
        try:
            me = await client.get_me()
            member = await client.get_chat_member(chat_id, me.id)
            return member.status in ["administrator", "creator"]
        except Exception:
            return False
    
    async def _has_recent_activity(self, client: Client, chat_id: int) -> bool:
        """Check if chat has recent messages"""
        try:
            # Get last message in chat
            messages = await client.get_chat_history(chat_id, limit=1)
            
            async for message in messages:
                if datetime.now() - message.date < timedelta(days=7):
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _is_new_chat(self, client: Client, chat_id: int) -> bool:
        """Check if chat is new (joined recently)"""
        try:
            me = await client.get_me()
            member = await client.get_chat_member(chat_id, me.id)
            
            if hasattr(member, 'joined_date') and member.joined_date:
                join_time = member.joined_date
                if datetime.now() - join_time < self.min_chat_age:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _leave_chat_safely(self, client: Client, chat_id: int) -> bool:
        """Leave a chat safely with error handling"""
        try:
            await client.leave_chat(chat_id)
            logger.info(f"👋 Left chat {chat_id}")
            
            # Update database
            await self._update_chat_status(chat_id, False)
            
            return True
            
        except FloodWait as e:
            logger.warning(f"Flood wait when leaving {chat_id}: {e.value}s")
            await asyncio.sleep(e.value)
            return False
            
        except (UserNotParticipant, ChannelInvalid):
            # Already left or invalid
            logger.debug(f"Already left/invalid chat {chat_id}")
            await self._update_chat_status(chat_id, False)
            return True
            
        except ChatAdminRequired:
            logger.warning(f"Cannot leave {chat_id}: Admin required")
            return False
            
        except PeerIdInvalid:
            logger.warning(f"Invalid peer ID: {chat_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error leaving chat {chat_id}: {e}")
            self.stats["errors"] += 1
            return False
    
    async def _update_chat_status(self, chat_id: int, active: bool):
        """Update chat status in database"""
        try:
            async with db_manager.get_session() as db:
                await db.active_chats.update_one(
                    {"chat_id": chat_id},
                    {
                        "$set": {
                            "active": active,
                            "updated_at": datetime.now(),
                            "left_at": None if active else datetime.now()
                        }
                    },
                    upsert=True
                )
        except Exception as e:
            logger.error(f"Failed to update chat status {chat_id}: {e}")
    
    async def _cleanup_recently_left(self):
        """Cleanup old entries from recently_left cache"""
        now = datetime.now()
        to_remove = []
        
        for chat_id, left_time in self.recently_left.items():
            if now - left_time > timedelta(days=7):  # Keep for 7 days
                to_remove.append(chat_id)
        
        for chat_id in to_remove:
            del self.recently_left[chat_id]
        
        if to_remove:
            logger.debug(f"Cleaned {len(to_remove)} entries from recently_left cache")
    
    async def _get_assistant_client(self, assistant_num: int):
        """Get assistant client"""
        from AviaxMusic.core.userbot import get_assistant
        
        try:
            return await get_assistant(assistant_num)
        except Exception as e:
            logger.error(f"Failed to get assistant {assistant_num}: {e}")
            return None
    
    async def _is_autoleave_enabled(self) -> bool:
        """Check if autoleave is enabled"""
        try:
            async with db_manager.get_session() as db:
                doc = await db.settings.find_one({"key": "autoleave"})
                return doc.get("value", True) if doc else True
        except Exception:
            return True
    
    async def get_stats(self) -> Dict:
        """Get autoleave statistics"""
        return {
            **self.stats,
            "whitelist_chats": len(self.whitelist_chats),
            "active_voice_chats": len(self.active_voice_chats),
            "recently_left": len(self.recently_left),
            "running": self.running
        }
    
    async def add_to_whitelist(self, chat_id: int) -> bool:
        """Add chat to whitelist"""
        try:
            self.whitelist_chats.add(chat_id)
            
            # Save to database
            async with db_manager.get_session() as db:
                await db.whitelist.update_one(
                    {"chat_id": chat_id},
                    {"$set": {"added_at": datetime.now()}},
                    upsert=True
                )
            
            logger.info(f"Added {chat_id} to whitelist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add to whitelist: {e}")
            return False
    
    async def remove_from_whitelist(self, chat_id: int) -> bool:
        """Remove chat from whitelist"""
        try:
            if chat_id in self.whitelist_chats:
                self.whitelist_chats.remove(chat_id)
            
            # Remove from database
            async with db_manager.get_session() as db:
                await db.whitelist.delete_one({"chat_id": chat_id})
            
            logger.info(f"Removed {chat_id} from whitelist")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove from whitelist: {e}")
            return False
    
    async def force_leave_chat(self, chat_id: int) -> bool:
        """Force leave a specific chat immediately"""
        from AviaxMusic.core.userbot import assistants
        
        for assistant_num in assistants:
            try:
                client = await self._get_assistant_client(assistant_num)
                if not client:
                    continue
                
                # Check if this assistant is in the chat
                try:
                    await client.get_chat(chat_id)
                except Exception:
                    continue  # Not in this chat
                
                # Leave the chat
                success = await self._leave_chat_safely(client, chat_id)
                if success:
                    return True
                    
            except Exception as e:
                logger.error(f"Force leave error for assistant {assistant_num}: {e}")
                continue
        
        return False


# Singleton instance
autoleave_manager = AutoLeaveManager()


async def start_autoleave():
    """Start autoleave monitoring"""
    await autoleave_manager.initialize()
    await autoleave_manager.start_monitoring()


async def stop_autoleave():
    """Stop autoleave monitoring"""
    await autoleave_manager.stop_monitoring()


async def get_autoleave_stats():
    """Get autoleave statistics"""
    return await autoleave_manager.get_stats()


async def whitelist_chat(chat_id: int) -> bool:
    """Add chat to whitelist"""
    return await autoleave_manager.add_to_whitelist(chat_id)


async def unwhitelist_chat(chat_id: int) -> bool:
    """Remove chat from whitelist"""
    return await autoleave_manager.remove_from_whitelist(chat_id)


async def force_leave(chat_id: int) -> bool:
    """Force leave a chat"""
    return await autoleave_manager.force_leave_chat(chat_id)