import random
import string

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pyrogram.errors import MessageNotModified
from pytgcalls.exceptions import NoActiveGroupCall, AlreadyJoinedError, NoAudioSourceFound

import config
from AviaxMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from AviaxMusic.core.call import Aviax
from AviaxMusic.utils import seconds_to_min, time_to_seconds
from AviaxMusic.utils.channelplay import get_channeplayCB
from AviaxMusic.utils.decorators.language import languageCB
from AviaxMusic.utils.decorators.play import PlayWrapper
from AviaxMusic.utils.formatters import formats
from AviaxMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from AviaxMusic.utils.logger import play_logs
from AviaxMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical


@app.on_message(
    filters.command(
        [
            "play",
            "vplay",
            "cplay",
            "cvplay",
            "playforce",
            "vplayforce",
            "cplayforce",
            "cvplayforce",
        ]
    )
    & filters.group
    & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(
    client,
    message: Message,
    _,
    chat_id,
    video,
    channel,
    playmode,
    url,
    fplay,
):
    mystic = await message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    plist_id = None
    slider = None
    plist_type = None
    spotify = None
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    audio_telegram = (
        (message.reply_to_message.audio or message.reply_to_message.voice)
        if message.reply_to_message
        else None
    )
    video_telegram = (
        (message.reply_to_message.video or message.reply_to_message.document)
        if message.reply_to_message
        else None
    )
    
    if audio_telegram:
        if audio_telegram.file_size > 104857600:  # 100MB limit
            try:
                return await mystic.edit_text(_["play_5"])
            except MessageNotModified:
                return
        duration_min = seconds_to_min(audio_telegram.duration)
        if audio_telegram.duration > config.DURATION_LIMIT:
            try:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                )
            except MessageNotModified:
                return
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(audio_telegram, audio=True)
            dur = await Telegram.get_duration(audio_telegram, file_path)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }

            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="telegram",
                    forceplay=fplay,
                )
            except Exception as e:
                print(f"Error in audio telegram play: {e}")
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
                try:
                    return await mystic.edit_text(err)
                except MessageNotModified:
                    return
            return await mystic.delete()
        return
    
    elif video_telegram:
        if message.reply_to_message.document:
            try:
                ext = video_telegram.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    try:
                        return await mystic.edit_text(
                            _["play_7"].format(f"{' | '.join(formats)}")
                        )
                    except MessageNotModified:
                        return
            except:
                try:
                    return await mystic.edit_text(
                        _["play_7"].format(f"{' | '.join(formats)}")
                    )
                except MessageNotModified:
                    return
        
        if video_telegram.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            try:
                return await mystic.edit_text(_["play_8"])
            except MessageNotModified:
                return
        
        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            message_link = await Telegram.get_link(message)
            file_name = await Telegram.get_filename(video_telegram)
            dur = await Telegram.get_duration(video_telegram, file_path)
            details = {
                "title": file_name,
                "link": message_link,
                "path": file_path,
                "dur": dur,
            }
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    video=True,
                    streamtype="telegram",
                    forceplay=fplay,
                )
            except Exception as e:
                print(f"Error in video telegram play: {e}")
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
                try:
                    return await mystic.edit_text(err)
                except MessageNotModified:
                    return
            return await mystic.delete()
        return
    
    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(
                        url,
                        config.PLAYLIST_FETCH_LIMIT,
                        message.from_user.id,
                    )
                except Exception as e:
                    print(f"Youtube playlist error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "playlist"
                plist_type = "yt"
                if "&" in url:
                    plist_id = (url.split("=")[1]).split("&")[0]
                else:
                    plist_id = url.split("=")[1]
                img = config.PLAYLIST_IMG_URL
                cap = _["play_9"]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except Exception as e:
                    print(f"Youtube track error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_10"].format(
                    details["title"],
                    details["duration_min"],
                )
        
        elif await Spotify.valid(url):
            spotify = True
            if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
                try:
                    return await mystic.edit_text(
                        "» Spotify is not supported yet.\n\nPlease try again later."
                    )
                except MessageNotModified:
                    return
            
            if "track" in url:
                try:
                    details, track_id = await Spotify.track(url)
                except Exception as e:
                    print(f"Spotify track error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            
            elif "playlist" in url:
                try:
                    details, plist_id = await Spotify.playlist(url)
                except Exception as e:
                    print(f"Spotify playlist error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "playlist"
                plist_type = "spplay"
                img = config.SPOTIFY_PLAYLIST_IMG_URL
                cap = _["play_11"].format(app.mention, message.from_user.mention)
            
            elif "album" in url:
                try:
                    details, plist_id = await Spotify.album(url)
                except Exception as e:
                    print(f"Spotify album error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "playlist"
                plist_type = "spalbum"
                img = config.SPOTIFY_ALBUM_IMG_URL
                cap = _["play_11"].format(app.mention, message.from_user.mention)
            
            elif "artist" in url:
                try:
                    details, plist_id = await Spotify.artist(url)
                except Exception as e:
                    print(f"Spotify artist error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "playlist"
                plist_type = "spartist"
                img = config.SPOTIFY_ARTIST_IMG_URL
                cap = _["play_11"].format(message.from_user.first_name)
            
            else:
                try:
                    return await mystic.edit_text(_["play_15"])
                except MessageNotModified:
                    return
        
        elif await Apple.valid(url):
            if "album" in url:
                try:
                    details, track_id = await Apple.track(url)
                except Exception as e:
                    print(f"Apple track error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "youtube"
                img = details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            
            elif "playlist" in url:
                spotify = True
                try:
                    details, plist_id = await Apple.playlist(url)
                except Exception as e:
                    print(f"Apple playlist error: {e}")
                    try:
                        return await mystic.edit_text(_["play_3"])
                    except MessageNotModified:
                        return
                streamtype = "playlist"
                plist_type = "apple"
                cap = _["play_12"].format(app.mention, message.from_user.mention)
                img = url
            
            else:
                try:
                    return await mystic.edit_text(_["play_3"])
                except MessageNotModified:
                    return
        
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
            except Exception as e:
                print(f"Resso error: {e}")
                try:
                    return await mystic.edit_text(_["play_3"])
                except MessageNotModified:
                    return
            streamtype = "youtube"
            img = details["thumb"]
            cap = _["play_10"].format(details["title"], details["duration_min"])
        
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
            except Exception as e:
                print(f"SoundCloud error: {e}")
                try:
                    return await mystic.edit_text(_["play_3"])
                except MessageNotModified:
                    return
            
            duration_sec = details["duration_sec"]
            if duration_sec > config.DURATION_LIMIT:
                try:
                    return await mystic.edit_text(
                        _["play_6"].format(
                            config.DURATION_LIMIT_MIN,
                            app.mention,
                        )
                    )
                except MessageNotModified:
                    return
            
            try:
                await stream(
                    _,
                    mystic,
                    user_id,
                    details,
                    chat_id,
                    user_name,
                    message.chat.id,
                    streamtype="soundcloud",
                    forceplay=fplay,
                )
            except Exception as e:
                print(f"SoundCloud stream error: {e}")
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
                try:
                    return await mystic.edit_text(err)
                except MessageNotModified:
                    return
            return await mystic.delete()
        
        else:
            # For index/m3u8 links
            try:
                await Aviax.stream_call(url)
            except NoActiveGroupCall:
                try:
                    await mystic.edit_text(_["black_9"])
                except MessageNotModified:
                    pass
                return await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=_["play_17"],
                )
            except Exception as e:
                print(f"Stream call error: {e}")
                try:
                    return await mystic.edit_text(_["general_2"].format(type(e).__name__))
                except MessageNotModified:
                    return
            
            try:
                await mystic.edit_text(_["str_2"])
            except MessageNotModified:
                pass
            
            try:
                await stream(
                    _,
                    mystic,
                    message.from_user.id,
                    url,
                    chat_id,
                    message.from_user.first_name,
                    message.chat.id,
                    video=video,
                    streamtype="index",
                    forceplay=fplay,
                )
            except Exception as e:
                print(f"Index stream error: {e}")
                ex_type = type(e).__name__
                err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
                try:
                    return await mystic.edit_text(err)
                except MessageNotModified:
                    return
            return await play_logs(message, streamtype="M3u8 or Index Link")
    
    else:
        # Text search (no URL provided)
        if len(message.command) < 2:
            buttons = botplaylist_markup(_)
            try:
                return await mystic.edit_text(
                    _["play_18"],
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
            except MessageNotModified:
                return
        
        slider = True
        query = message.text.split(None, 1)[1]
        if "-v" in query:
            query = query.replace("-v", "")
        
        try:
            details, track_id = await YouTube.track(query)
        except Exception as e:
            print(f"Youtube search error: {e}")
            try:
                return await mystic.edit_text(_["play_3"])
            except MessageNotModified:
                return
        
        streamtype = "youtube"
    
    # Handle direct play or playlist queuing
    if str(playmode) == "Direct":
        if not plist_type:
            if details["duration_min"]:
                duration_sec = time_to_seconds(details["duration_min"])
                if duration_sec > config.DURATION_LIMIT:
                    try:
                        return await mystic.edit_text(
                            _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                        )
                    except MessageNotModified:
                        return
            else:
                # Live stream handling
                buttons = livestream_markup(
                    _,
                    track_id,
                    user_id,
                    "v" if video else "a",
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                try:
                    return await mystic.edit_text(
                        _["play_13"],
                        reply_markup=InlineKeyboardMarkup(buttons),
                    )
                except MessageNotModified:
                    return
        
        # Play directly
        try:
            await stream(
                _,
                mystic,
                user_id,
                details,
                chat_id,
                user_name,
                message.chat.id,
                video=video,
                streamtype=streamtype,
                spotify=spotify,
                forceplay=fplay,
            )
        except Exception as e:
            print(f"Direct play error: {e}")
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
            try:
                return await mystic.edit_text(err)
            except MessageNotModified:
                return
        
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    
    else:
        # Add to playlist/queue
        if plist_type:
            ran_hash = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=10)
            )
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(
                _,
                ran_hash,
                message.from_user.id,
                plist_type,
                "c" if channel else "g",
                "f" if fplay else "d",
            )
            await mystic.delete()
            await message.reply_photo(
                photo=img,
                caption=cap,
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            return await play_logs(message, streamtype=f"Playlist : {plist_type}")
        
        else:
            if slider:
                buttons = slider_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    query,
                    0,
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                await mystic.delete()
                await message.reply_photo(
                    photo=details["thumb"],
                    caption=_["play_10"].format(
                        details["title"].title(),
                        details["duration_min"],
                    ),
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(message, streamtype=f"Searched on Youtube")
            
            else:
                buttons = track_markup(
                    _,
                    track_id,
                    message.from_user.id,
                    "c" if channel else "g",
                    "f" if fplay else "d",
                )
                await mystic.delete()
                await message.reply_photo(
                    photo=img,
                    caption=cap,
                    reply_markup=InlineKeyboardMarkup(buttons),
                )
                return await play_logs(message, streamtype=f"URL Searched Inline")


@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = callback_request.split("|")
    
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    
    user_name = CallbackQuery.from_user.first_name
    
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    
    try:
        details, track_id = await YouTube.track(vidid, True)
    except Exception as e:
        print(f"Callback YouTube track error: {e}")
        try:
            return await mystic.edit_text(_["play_3"])
        except MessageNotModified:
            return
    
    if details["duration_min"]:
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            try:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                )
            except MessageNotModified:
                return
    else:
        # Live stream handling
        buttons = livestream_markup(
            _,
            track_id,
            CallbackQuery.from_user.id,
            mode,
            "c" if cplay == "c" else "g",
            "f" if fplay else "d",
        )
        try:
            return await mystic.edit_text(
                _["play_13"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            return
    
    video = True if mode == "v" else None
    ffplay = True if fplay == "f" else None
    
    try:
        await stream(
            _,
            mystic,
            CallbackQuery.from_user.id,
            details,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="youtube",
            forceplay=ffplay,
        )
    except Exception as e:
        print(f"Callback stream error: {e}")
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        try:
            return await mystic.edit_text(err)
        except MessageNotModified:
            return
    
    return await mystic.delete()


@app.on_callback_query(filters.regex("AnonymousAdmin") & ~BANNED_USERS)
async def anonymous_check(client, CallbackQuery):
    try:
        await CallbackQuery.answer(
            "» Revert back to user account:\n\nOpen your group settings.\n-> Administrators\n-> Click on your name\n-> Uncheck anonymous admin permissions.",
            show_alert=True,
        )
    except:
        pass


@app.on_callback_query(filters.regex("AviaxPlaylists") & ~BANNED_USERS)
@languageCB
async def play_playlists_command(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    (
        videoid,
        user_id,
        ptype,
        mode,
        cplay,
        fplay,
    ) = callback_request.split("|")
    
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    
    user_name = CallbackQuery.from_user.first_name
    
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    
    try:
        if ptype == "yt":
            playlists = await YouTube.playlist(
                videoid,
                config.PLAYLIST_FETCH_LIMIT,
                CallbackQuery.from_user.id,
            )
        elif ptype == "spplay":
            playlists = await Spotify.playlist(videoid)
        elif ptype == "spalbum":
            playlists = await Spotify.album(videoid)
        elif ptype == "spartist":
            playlists = await Spotify.artist(videoid)
        elif ptype == "apple":
            playlists = await Apple.playlist(videoid, config.PLAYLIST_FETCH_LIMIT)
        else:
            try:
                return await mystic.edit_text(_["play_3"])
            except MessageNotModified:
                return
    except Exception as e:
        print(f"Error fetching playlist: {e}")
        try:
            return await mystic.edit_text(_["play_3"])
        except MessageNotModified:
            return
    
    if not playlists:
        try:
            return await mystic.edit_text(_["play_3"])
        except MessageNotModified:
            return
    
    streamtype = "playlist"
    plist_type = ptype
    
    try:
        await stream(
            _,
            mystic,
            user_id,
            playlists,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video=True if mode == "v" else None,
            streamtype=streamtype,
            spotify=True if ptype in ["spplay", "spalbum", "spartist"] else False,
            forceplay=True if fplay == "f" else False,
        )
    except Exception as e:
        print(f"Error in play_playlists_command: {e}")
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        try:
            return await mystic.edit_text(err)
        except MessageNotModified:
            return
    
    return await mystic.delete()


@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, rtype, query, user_id, cplay, fplay = callback_request.split("|")
    
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    
    what_list = what.split("|")
    rtype = rtype.split("|")
    if what_list[0] == "F":
        try:
            await CallbackQuery.answer("Fetching PlayList....", show_alert=True)
        except:
            pass
        (
            videoid,
            user_id,
            ptype,
            mode,
            cplay,
            fplay,
        ) = callback_request.split("|")
        playlist_id = ptype.split("-")[1]
        await CallbackQuery.message.delete()
        buttons = playlist_markup(
            _,
            playlist_id,
            CallbackQuery.from_user.id,
            ptype,
            "c" if cplay == "c" else "g",
            "f" if fplay == "f" else "d",
        )
        await CallbackQuery.message.reply_photo(
            photo=config.SPOTIFY_ARTIST_IMG_URL
            if ptype == "spartist"
            else config.TELEGRAM_AUDIO_URL
            if ptype == "telegram"
            else config.SPOTIFY_ALBUM_IMG_URL
            if ptype == "spalbum"
            else config.PLAYLIST_IMG_URL,
            caption="**Usage:** /play [song name or youtube link or reply to audio]\n\nIf you want to play playlists! Select the one from below.",
            reply_markup=InlineKeyboardMarkup(buttons),
        )
        return
    
    try:
        await CallbackQuery.answer()
    except:
        pass
    
    if what_list[0] == "T":
        if rtype[0] == "t":
            query_type = 0
        else:
            query_type = 1
        await CallbackQuery.message.delete()
        results = await YouTube.inline_query(query, query_type)
        if results:
            await app.send_inline_bot_result(
                CallbackQuery.message.chat.id,
                results[0].id,
                reply_to_message_id=CallbackQuery.message.id,
            )
        return
    
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    
    try:
        await CallbackQuery.message.delete()
    except:
        pass
    
    mystic = await CallbackQuery.message.reply_text(_["play_1"])
    
    try:
        details, track_id = await YouTube.track(query)
    except:
        try:
            return await mystic.edit_text(_["play_3"])
        except MessageNotModified:
            return
    
    if details["duration_min"]:
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            try:
                return await mystic.edit_text(
                    _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
                )
            except MessageNotModified:
                return
    else:
        buttons = livestream_markup(
            _,
            track_id,
            CallbackQuery.from_user.id,
            "v" if rtype[0] == "v" else "a",
            "c" if cplay == "c" else "g",
            "f" if fplay else "d",
        )
        try:
            return await mystic.edit_text(
                _["play_13"],
                reply_markup=InlineKeyboardMarkup(buttons),
            )
        except MessageNotModified:
            return
    
    video = True if rtype[0] == "v" else None
    ffplay = True if fplay == "f" else None
    
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    
    try:
        await stream(
            _,
            mystic,
            user_id,
            details,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="youtube",
            forceplay=ffplay,
        )
    except Exception as e:
        print(f"Slider stream error: {e}")
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        try:
            return await mystic.edit_text(err)
        except MessageNotModified:
            return
    
    return await mystic.delete()