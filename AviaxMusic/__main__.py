"""
Aviax Music Bot - Production Version
PyTgCalls v3 Ready with Enhanced Error Handling
"""

import asyncio
import importlib
import logging
import time
import signal
import sys
import psutil
from collections import defaultdict
from typing import Dict, List, Optional, Set
from contextlib import asynccontextmanager

from pyrogram import Client, idle
from pyrogram.errors import FloodWait, RPCError
from pytgcalls import PyTgCallsClient
from pytgcalls.exceptions import (
    NoActiveGroupCall, 
    AlreadyJoinedError,
    NotJoinedError,
    GroupCallNotFound
)
from pytgcalls.types import AudioParameters, AudioQuality

# Configuration
import config
from AviaxMusic.misc import sudo
from AviaxMusic.utils.database import get_banned_users, get_gbanned

# ===================== LOGGING CONFIGURATION =====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aviax_production.log'),
        logging.StreamHandler()
    ]
)

# Set specific log levels
logging.getLogger('pyrogram').setLevel(logging.WARNING)
logging.getLogger('pytgcalls').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('aiohttp').setLevel(logging.WARNING)

LOGGER = logging.getLogger("AviaxMusic")

# ===================== RATE LIMITING =====================
class RateLimiter:
    """Rate limiter for commands"""
    
    def __init__(self):
        self.user_limits = defaultdict(list)
        self.chat_limits = defaultdict(list)
        self.command_cooldowns = {}
        
    def is_rate_limited(self, user_id: int, chat_id: int, 
                       max_user: int = 3, max_chat: int = 5,
                       user_window: int = 30, chat_window: int = 10) -> bool:
        """Check if user/chat is rate limited"""
        current_time = time.time()
        
        # Clean old entries
        self.user_limits[user_id] = [
            t for t in self.user_limits[user_id] 
            if current_time - t < user_window
        ]
        
        self.chat_limits[chat_id] = [
            t for t in self.chat_limits[chat_id] 
            if current_time - t < chat_window
        ]
        
        # Check limits
        if len(self.user_limits[user_id]) >= max_user:
            return True
            
        if len(self.chat_limits[chat_id]) >= max_chat:
            return True
            
        # Add current request
        self.user_limits[user_id].append(current_time)
        self.chat_limits[chat_id].append(current_time)
        return False
    
    def add_command(self, chat_id: int, cooldown: float = 1.0) -> bool:
        """Add command with cooldown"""
        current_time = time.time()
        
        if chat_id in self.command_cooldowns:
            time_since_last = current_time - self.command_cooldowns[chat_id]
            if time_since_last < cooldown:
                return False
                
        self.command_cooldowns[chat_id] = current_time
        return True

# ===================== ERROR HANDLER =====================
class UserErrorHandler:
    """User-friendly error messages"""
    
    ERROR_MESSAGES = {
        'NoActiveGroupCall': "🔇 No active voice chat found. Please start a voice chat first!",
        'NotInGroupCall': "🚫 I'm not in the voice chat. Please add me first!",
        'DownloadError': "❌ Failed to download the media. Please try another source.",
        'InvalidUrl': "🔗 Invalid URL provided. Please check and try again.",
        'QueueFull': "📊 Queue is full. Please wait for current songs to finish.",
        'PermissionError': "🔒 I don't have permission to join the voice chat.",
        'Timeout': "⏰ Request timed out. Please try again.",
        'RateLimited': "⏱️ Too many requests. Please wait a moment.",
        'Generic': "⚠️ An error occurred. Please try again or contact support."
    }
    
    @staticmethod
    async def send_error(client, message, error_type: str, details: str = None):
        """Send user-friendly error message"""
        error_msg = UserErrorHandler.ERROR_MESSAGES.get(
            error_type, 
            UserErrorHandler.ERROR_MESSAGES['Generic']
        )
        
        if details:
            error_msg += f"\n\n📝 Details: {details[:100]}..."
            
        try:
            await message.reply(error_msg)
        except FloodWait as e:
            await asyncio.sleep(e.value)
            await message.reply(error_msg)
        except Exception:
            LOGGER.error(f"Failed to send error message to {message.chat.id}")
        
        # Log full error for debugging
        LOGGER.error(f"User Error: {error_type} - Details: {details}")

# ===================== RESOURCE MONITOR =====================
class ResourceMonitor:
    """Monitor system resources"""
    
    def __init__(self, max_cpu: float = 80.0, max_memory: float = 85.0):
        self.max_cpu = max_cpu
        self.max_memory = max_memory
        self._throttle_mode = False
        
    async def monitor_loop(self):
        """Monitor resources in background"""
        while True:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory_percent = psutil.virtual_memory().percent
                
                if cpu_percent > self.max_cpu or memory_percent > self.max_memory:
                    if not self._throttle_mode:
                        LOGGER.warning(
                            f"High resource usage - CPU: {cpu_percent}%, "
                            f"Memory: {memory_percent}%. Entering throttle mode."
                        )
                        self._throttle_mode = True
                else:
                    if self._throttle_mode:
                        LOGGER.info("Resource usage normal. Exiting throttle mode.")
                        self._throttle_mode = False
                        
            except Exception as e:
                LOGGER.error(f"Resource monitor error: {e}")
                
            await asyncio.sleep(30)

# ===================== AVIAX CALL HANDLER =====================
class AviaxCall(PyTgCallsClient):
    """Enhanced PyTgCalls client with auto-recovery"""
    
    def __init__(self, app: Client):
        super().__init__(
            cache_duration=100,
            overload_quiet_mode=True
        )
        self.app = app
        self._reconnect_attempts = defaultdict(int)
        self._max_reconnect_attempts = 3
        self._active_chats: Set[int] = set()
        self._play_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        self._join_locks: Dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)
        
    async def safe_join(self, chat_id: int) -> bool:
        """Safely join voice chat with retry logic"""
        async with self._join_locks[chat_id]:
            if chat_id in self._active_chats:
                return True
                
            for attempt in range(self._max_reconnect_attempts):
                try:
                    await self.join_group_call(
                        chat_id,
                        AudioParameters.from_quality(AudioQuality.HIGH)
                    )
                    self._active_chats.add(chat_id)
                    self._reconnect_attempts[chat_id] = 0
                    LOGGER.info(f"Successfully joined voice chat {chat_id}")
                    return True
                    
                except NoActiveGroupCall:
                    LOGGER.warning(f"No active group call in {chat_id}, attempt {attempt + 1}")
                    await asyncio.sleep(2 ** attempt)
                    continue
                    
                except AlreadyJoinedError:
                    self._active_chats.add(chat_id)
                    return True
                    
                except Exception as e:
                    LOGGER.error(f"Join attempt {attempt + 1} failed for {chat_id}: {e}")
                    await asyncio.sleep(2 ** attempt)
                    
            LOGGER.error(f"Failed to join chat {chat_id} after {self._max_reconnect_attempts} attempts")
            return False
    
    async def safe_leave(self, chat_id: int):
        """Safely leave voice chat"""
        try:
            await self.leave_group_call(chat_id)
            self._active_chats.discard(chat_id)
            LOGGER.info(f"Left voice chat {chat_id}")
        except Exception as e:
            LOGGER.error(f"Error leaving voice chat {chat_id}: {e}")
    
    async def handle_disconnect(self, chat_id: int):
        """Handle voice chat disconnection"""
        if chat_id in self._active_chats:
            self._active_chats.remove(chat_id)
            
        # Attempt to rejoin if conditions are met
        self._reconnect_attempts[chat_id] += 1
        if self._reconnect_attempts[chat_id] <= self._max_reconnect_attempts:
            LOGGER.info(f"Attempting to reconnect to {chat_id}")
            await asyncio.sleep(5)
            await self.safe_join(chat_id)
        else:
            LOGGER.error(f"Max reconnection attempts reached for {chat_id}")
    
    async def stream_call(self, chat_id: int, file_path: str):
        """Safe stream with lock protection"""
        async with self._play_locks[chat_id]:
            try:
                if not await self.safe_join(chat_id):
                    raise NoActiveGroupCall("Failed to join voice chat")
                    
                # Start streaming
                await self.start_audio_stream(
                    chat_id,
                    file_path,
                    audio_parameters=AudioParameters.from_quality(AudioQuality.HIGH)
                )
                return True
                
            except NoActiveGroupCall as e:
                LOGGER.error(f"No active group call in {chat_id}")
                raise
                
            except Exception as e:
                LOGGER.error(f"Stream error in {chat_id}: {e}")
                await self.handle_disconnect(chat_id)
                raise

# ===================== SECURITY DECORATORS =====================
class SecurityDecorators:
    """Security and rate limiting decorators"""
    
    def __init__(self, rate_limiter: RateLimiter):
        self.rate_limiter = rate_limiter
        
    def command_protection(self, user_limit: int = 5, chat_limit: int = 10):
        """Decorator for command protection"""
        def decorator(func):
            async def wrapper(client, message, *args, **kwargs):
                # Check rate limits
                if self.rate_limiter.is_rate_limited(
                    message.from_user.id, 
                    message.chat.id,
                    max_user=user_limit,
                    max_chat=chat_limit
                ):
                    await UserErrorHandler.send_error(
                        client, message, 'RateLimited'
                    )
                    return
                
                # Check command cooldown
                if not self.rate_limiter.add_command(message.chat.id):
                    await asyncio.sleep(1)
                
                # Execute command
                try:
                    return await func(client, message, *args, **kwargs)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    return await func(client, message, *args, **kwargs)
                except Exception as e:
                    LOGGER.error(f"Command error: {e}")
                    await UserErrorHandler.send_error(
                        client, message, 'Generic', str(e)
                    )
            return wrapper
        return decorator

# ===================== LIFESPAN MANAGER =====================
@asynccontextmanager
async def bot_lifespan():
    """Manage bot startup and shutdown"""
    LOGGER.info("🚀 Starting Aviax Music Bot...")
    
    # Setup signal handlers
    loop = asyncio.get_event_loop()
    shutdown_event = asyncio.Event()
    
    def signal_handler():
        LOGGER.info("🛑 Received shutdown signal")
        shutdown_event.set()
    
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        yield shutdown_event
    finally:
        LOGGER.info("🧹 Performing cleanup...")
        shutdown_event.set()

# ===================== MAIN INITIALIZATION =====================
async def init():
    """Main initialization function"""
    
    async with bot_lifespan() as shutdown_event:
        # ========== VALIDATE CONFIGURATION ==========
        if not any([
            config.STRING1, config.STRING2, config.STRING3,
            config.STRING4, config.STRING5
        ]):
            LOGGER.error("Assistant client variables not defined, exiting...")
            return
        
        # ========== INITIALIZE COMPONENTS ==========
        # Rate limiter
        rate_limiter = RateLimiter()
        
        # Security decorators
        security = SecurityDecorators(rate_limiter)
        
        # Resource monitor
        resource_monitor = ResourceMonitor()
        
        # Initialize apps
        try:
            app = Client(
                "AviaxMusic",
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                bot_token=config.BOT_TOKEN,
                plugins=dict(root="AviaxMusic.plugins")
            )
            
            # Userbot clients (simplified - you need to implement properly)
            userbots = []
            string_sessions = [
                config.STRING1, config.STRING2, config.STRING3,
                config.STRING4, config.STRING5
            ]
            
            for i, session in enumerate(string_sessions, 1):
                if session:
                    try:
                        userbot = Client(
                            f"AviaxAssistent{i}",
                            session_string=session,
                            api_id=config.API_ID,
                            api_hash=config.API_HASH
                        )
                        userbots.append(userbot)
                        LOGGER.info(f"Initialized assistant client {i}")
                    except Exception as e:
                        LOGGER.error(f"Failed to initialize assistant {i}: {e}")
            
            if not userbots:
                LOGGER.error("No valid assistant clients, exiting...")
                return
                
        except Exception as e:
            LOGGER.error(f"Failed to initialize clients: {e}")
            return
        
        # ========== LOAD BANNED USERS ==========
        BANNED_USERS = set()
        try:
            users = await get_gbanned()
            for user_id in users:
                BANNED_USERS.add(user_id)
            
            users = await get_banned_users()
            for user_id in users:
                BANNED_USERS.add(user_id)
                
            LOGGER.info(f"Loaded {len(BANNED_USERS)} banned users")
        except Exception as e:
            LOGGER.error(f"Failed to load banned users: {e}")
        
        # ========== START APPS ==========
        try:
            await app.start()
            LOGGER.info("Bot client started")
            
            for ub in userbots:
                await ub.start()
                LOGGER.info(f"Assistant {ub.name} started")
                
        except Exception as e:
            LOGGER.error(f"Failed to start clients: {e}")
            return
        
        # ========== LOAD PLUGINS ==========
        try:
            # Import all modules
            from AviaxMusic.plugins import ALL_MODULES
            for module_name in ALL_MODULES:
                try:
                    importlib.import_module(f"AviaxMusic.plugins.{module_name}")
                    LOGGER.debug(f"Loaded module: {module_name}")
                except Exception as e:
                    LOGGER.error(f"Failed to load module {module_name}: {e}")
                    
            LOGGER.info(f"Successfully imported {len(ALL_MODULES)} modules")
        except Exception as e:
            LOGGER.error(f"Failed to load plugins: {e}")
        
        # ========== INITIALIZE PYTGCALLS ==========
        try:
            # Use the first userbot for calls
            call_client = AviaxCall(userbots[0])
            
            # Start resource monitor
            monitor_task = asyncio.create_task(resource_monitor.monitor_loop())
            
            # Test voice chat
            test_chat_id = config.LOG_GROUP_ID
            if test_chat_id:
                try:
                    await call_client.safe_join(test_chat_id)
                    # Test stream
                    await call_client.stream_call(
                        test_chat_id,
                        "https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4"
                    )
                    LOGGER.info("Voice chat test successful")
                except NoActiveGroupCall:
                    LOGGER.error(
                        "Please turn on the videochat of your log group/channel."
                    )
                    # Don't exit - let bot run without voice test
                except Exception as e:
                    LOGGER.warning(f"Voice test failed: {e}")
            
        except Exception as e:
            LOGGER.error(f"Failed to initialize voice client: {e}")
        
        # ========== BOT INFO ==========
        bot = await app.get_me()
        LOGGER.info(f"""
╔═══════════════════════════════════════════════════╗
║                AVIAX MUSIC BOT                    ║
╠═══════════════════════════════════════════════════╣
║  Bot: @{bot.username}                             ║
║  ID: {bot.id}                                     ║
║  Assistants: {len(userbots)} active               ║
║  Banned Users: {len(BANNED_USERS)}                ║
║  PyTgCalls: v3 Ready                             ║
║  Status: PRODUCTION                              ║
╚═══════════════════════════════════════════════════╝
        """)
        
        # ========== MAIN LOOP ==========
        try:
            # Run idle until shutdown signal
            while not shutdown_event.is_set():
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            LOGGER.info("Keyboard interrupt received")
        except Exception as e:
            LOGGER.error(f"Main loop error: {e}")
        
        # ========== GRACEFUL SHUTDOWN ==========
        LOGGER.info("🛑 Initiating graceful shutdown...")
        
        # Stop resource monitor
        if 'monitor_task' in locals():
            monitor_task.cancel()
            try:
                await monitor_task
            except asyncio.CancelledError:
                pass
        
        # Stop call client
        if 'call_client' in locals():
            for chat_id in list(call_client._active_chats):
                try:
                    await call_client.safe_leave(chat_id)
                except Exception as e:
                    LOGGER.error(f"Error leaving chat {chat_id}: {e}")
        
        # Stop userbots
        for ub in userbots:
            try:
                await ub.stop()
                LOGGER.info(f"Stopped assistant {ub.name}")
            except Exception as e:
                LOGGER.error(f"Error stopping assistant: {e}")
        
        # Stop main app
        try:
            await app.stop()
            LOGGER.info("Stopped bot client")
        except Exception as e:
            LOGGER.error(f"Error stopping bot: {e}")
        
        LOGGER.info("✅ Shutdown complete")

# ===================== ENTRY POINT =====================
if __name__ == "__main__":
    # Set event loop policy for Windows compatibility
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Increase recursion limit for deep call stacks
    sys.setrecursionlimit(10**6)
    
    # Run the bot
    try:
        asyncio.run(init())
    except KeyboardInterrupt:
        LOGGER.info("Bot stopped by user")
    except Exception as e:
        LOGGER.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)