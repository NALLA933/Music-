import asyncio
import os
import re
import json
import tempfile
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds
import os
import glob
import random
import logging
import aiohttp
import config
from config import API_URL, VIDEO_API_URL, API_KEY


def cookie_txt_file(cookies_file=None):
    # If cookies_file is provided, use it
    if cookies_file and os.path.exists(cookies_file):
        return cookies_file
    
    # Fallback to random cookie from cookies directory
    cookie_dir = f"{os.getcwd()}/cookies"
    if not os.path.exists(cookie_dir):
        return None
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]
    if not cookies_files:
        return None
    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file


async def download_song(link: str, cookies_file=None):
    video_id = link.split('v=')[-1].split('&')[0]

    download_folder = "downloads"
    for ext in ["mp3", "m4a", "webm"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            #print(f"File already exists: {file_path}")
            return file_path
        
    # ===== INSTANT VC JOINING: GET DIRECT AUDIO URL =====
    # Use yt-dlp with --get-url to fetch direct audio URL (bypasses API & downloads)
    cookie_file = cookie_txt_file(cookies_file)
    if not cookie_file:
        print("No cookies found for audio download.")
        # Fallback to yt-dlp download
        return await yt_dlp_download_audio(link, cookies_file)
    
    # Build yt-dlp command for direct URL fetching with updated options
    cmd = [
        "yt-dlp",
        "--get-url",                     # Get URL instead of downloading
        "-f", "bestaudio/best",          # Best audio format
        "--cookies", cookie_file,        # Use cookies for age-restricted content
        "--age-limit", "25",             # Bypass age restriction
        "--geo-bypass",                  # Bypass geographic restrictions
        "--ignore-errors",               # Continue on errors
        "--no-check-certificate",        # Don't check SSL certificate
        "--quiet",                       # Quiet mode
        "--extractor-args", "youtube:player_client=android,web",  # Fix signature issues
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",  # Modern UA
        link
    ]
    
    try:
        # Execute with timeout to prevent hanging
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Timeout after 5 seconds (adjust as needed)
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=5.0)
        
        if proc.returncode != 0:
            print(f"[FAIL] yt-dlp --get-url failed: {stderr.decode()}")
            # Fallback to regular download
            return await yt_dlp_download_audio(link, cookies_file)
        
        direct_url = stdout.decode().strip()
        if not direct_url:
            print("[FAIL] No direct URL obtained from yt-dlp.")
            return await yt_dlp_download_audio(link, cookies_file)
        
        print(f"[SUCCESS] Got direct audio URL: {direct_url[:80]}...")
        return direct_url  # Return direct URL for instant streaming
        
    except asyncio.TimeoutError:
        print("[FAIL] yt-dlp --get-url timeout (5s), falling back to download.")
        return await yt_dlp_download_audio(link, cookies_file)
    except Exception as e:
        print(f"[FAIL] Error getting direct audio URL: {e}")
        return await yt_dlp_download_audio(link, cookies_file)


async def yt_dlp_download_audio(link: str, cookies_file=None):
    """Fallback audio download using yt-dlp with cookies"""
    cookie_file = cookie_txt_file(cookies_file)
    if not cookie_file:
        print("No cookies found for audio download fallback.")
        return None
    
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookie_file,
            "extract_flat": False,
            "skip_download": False,  # We want to download
            "nocheckcertificate": True,
            # Added options for age-restricted content
            "age_limit": 25,
            "geo_bypass": True,
            "ignoreerrors": True,
            # Modern user agent to bypass bot detection
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            # Fix signature issues
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            # Change extension if needed
            if not os.path.exists(file_path):
                # Try to find the actual file
                base_path = os.path.splitext(file_path)[0]
                for ext in ['.webm', '.m4a', '.mp3', '.opus']:
                    if os.path.exists(base_path + ext):
                        return base_path + ext
            return file_path
    except Exception as e:
        print(f"yt-dlp audio download failed: {e}")
        return None


async def download_video(link: str, cookies_file=None):
    video_id = link.split('v=')[-1].split('&')[0]

    download_folder = "downloads"
    for ext in ["mp4", "webm", "mkv"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            return file_path
        
    # Try API first with 20 second timeout
    video_url = f"{VIDEO_API_URL}/video/{video_id}?api={API_KEY}"
    async with aiohttp.ClientSession() as session:
        for attempt in range(10):
            try:
                # Add 20 second timeout for API response
                timeout = aiohttp.ClientTimeout(total=20)
                async with session.get(video_url, timeout=timeout) as response:
                    if response.status != 200:
                        raise Exception(f"API request failed with status code {response.status}")
                
                    data = await response.json()
                    status = data.get("status", "").lower()

                    if status == "done":
                        download_url = data.get("link")
                        if not download_url:
                            raise Exception("API response did not provide a download URL.")
                        break
                    elif status == "downloading":
                        await asyncio.sleep(8)
                    else:
                        error_msg = data.get("error") or data.get("message") or f"Unexpected status '{status}'"
                        raise Exception(f"API error: {error_msg}")
            except asyncio.TimeoutError:
                print("⏱️ API timeout after 20 seconds, falling back to yt-dlp")
                # Fallback to yt-dlp with cookies
                return await yt_dlp_download_video(link, cookies_file)
            except Exception as e:
                print(f"[FAIL] {e}")
                # Fallback to yt-dlp with cookies
                return await yt_dlp_download_video(link, cookies_file)
        else:
            print("⏱️ Max retries reached. Still downloading...")
            # Fallback to yt-dlp with cookies
            return await yt_dlp_download_video(link, cookies_file)

        try:
            file_format = data.get("format", "mp4")
            file_extension = file_format.lower()
            file_name = f"{video_id}.{file_extension}"
            download_folder = "downloads"
            os.makedirs(download_folder, exist_ok=True)
            file_path = os.path.join(download_folder, file_name)

            async with session.get(download_url) as file_response:
                with open(file_path, 'wb') as f:
                    while True:
                        chunk = await file_response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                return file_path
        except aiohttp.ClientError as e:
            print(f"Network or client error occurred while downloading: {e}")
            # Fallback to yt-dlp with cookies
            return await yt_dlp_download_video(link, cookies_file)
        except Exception as e:
            print(f"Error occurred while downloading video: {e}")
            # Fallback to yt-dlp with cookies
            return await yt_dlp_download_video(link, cookies_file)
    return await yt_dlp_download_video(link, cookies_file)


async def yt_dlp_download_video(link: str, cookies_file=None):
    """Fallback video download using yt-dlp with cookies"""
    cookie_file = cookie_txt_file(cookies_file)
    if not cookie_file:
        print("No cookies found for video download fallback.")
        return None
    
    try:
        ydl_opts = {
            "format": "bestvideo[height<=?720][width<=?1280]+bestaudio/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "cookiefile": cookie_file,
            "extract_flat": False,
            "skip_download": False,
            "nocheckcertificate": True,
            "merge_output_format": "mp4",
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            # Added options for signature solving
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },
            # Other options
            "age_limit": 25,
            "geo_bypass": True,
            "ignoreerrors": True,
            # Modern user agent to bypass bot detection
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            file_path = ydl.prepare_filename(info)
            # Ensure it's mp4
            if not file_path.endswith('.mp4'):
                mp4_path = os.path.splitext(file_path)[0] + '.mp4'
                if os.path.exists(mp4_path):
                    return mp4_path
            return file_path
    except Exception as e:
        print(f"yt-dlp video download failed: {e}")
        return None


async def check_file_size(link, cookies_file=None):
    async def get_format_info(link):
        cookie_file = cookie_txt_file(cookies_file)
        if not cookie_file:
            print("No cookies found. Cannot check file size.")
            return None
            
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_file,
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--age-limit", "25",
            "--geo-bypass",
            "--ignore-errors",
            "--no-check-certificate",
            "--quiet",
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size


async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None, cookies_file=None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # First try using VideosSearch
        try:
            results = VideosSearch(link, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration_min = result["duration"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                vidid = result["id"]
                if str(duration_min) == "None":
                    duration_sec = 0
                else:
                    duration_sec = int(time_to_seconds(duration_min))
                return title, duration_min, duration_sec, thumbnail, vidid
        except Exception as e:
            print(f"VideosSearch failed (possibly age-restricted): {e}")
        
        # Fallback to yt-dlp with cookies - especially for age-restricted content like "I'm done" by Manu
        cookie_file = cookie_txt_file(cookies_file)
        if cookie_file:
            try:
                ydl_opts = {
                    "quiet": True,
                    "no_warnings": True,
                    "cookiefile": cookie_file,
                    "extract_flat": True,  # FAST METADATA EXTRACTION
                    "nocheckcertificate": True,
                    # Added options for age-restricted content
                    "age_limit": 25,
                    "geo_bypass": True,
                    "ignoreerrors": True,
                    # Modern user agent
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    # Fix signature issues
                    "extractor_args": {
                        "youtube": {
                            "player_client": ["android", "web"]
                        }
                    },
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(link, download=False)
                    title = info.get('title', 'Unknown Title')
                    duration_sec = info.get('duration', 0)
                    duration_min = f"{duration_sec // 60}:{duration_sec % 60:02d}" if duration_sec else "0:00"
                    thumbnail = info.get('thumbnail', '')
                    vidid = info.get('id', link.split('v=')[-1].split('&')[0])
                    return title, duration_min, duration_sec, thumbnail, vidid
            except Exception as e:
                print(f"yt-dlp details failed: {e}")
        
        # Return default values if both methods fail
        return "Unknown Title", "0:00", 0, "", link.split('v=')[-1].split('&')[0] if 'v=' in link else ""

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None, cookies_file=None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        # Try video API first
        try:
            downloaded_file = await download_video(link, cookies_file)
            if downloaded_file:
                return 1, downloaded_file
        except Exception as e:
            print(f"Video API failed: {e}")
        
        # Fallback to cookies
        cookie_file = cookie_txt_file(cookies_file)
        if not cookie_file:
            return 0, "No cookies found. Cannot download video."
        
        # Updated command with new options
        cmd = [
            "yt-dlp",
            "--cookies", cookie_file,
            "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--age-limit", "25",
            "--geo-bypass",
            "--ignore-errors",
            "--no-check-certificate",
            "--quiet",
            "--extractor-args", "youtube:player_client=android,web",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link
        ]
            
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None, cookies_file=None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file(cookies_file)
        if not cookie_file:
            return []
        
        # Updated command with new options
        cmd = f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_file} "
        cmd += "--user-agent 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36' "
        cmd += "--age-limit 25 --geo-bypass --ignore-errors --no-check-certificate --quiet "
        cmd += "--extractor-args youtube:player_client=android,web "
        cmd += f"--playlist-end {limit} --skip-download {link}"
        
        playlist = await shell_cmd(cmd)
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None, cookies_file=None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        
        cookie_file = cookie_txt_file(cookies_file)
        if not cookie_file:
            return [], link
            
        ytdl_opts = {
            "quiet": True, 
            "cookiefile": cookie_file,
            "nocheckcertificate": True,
            "extract_flat": False,
            "skip_download": True,
            # Added options for signature solving
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web"]
                }
            },
            # Other options
            "age_limit": 25,
            "geo_bypass": True,
            "ignoreerrors": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        }
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
        cookies_file: Union[str, None] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        
        def audio_dl():
            cookie_file = cookie_txt_file(cookies_file)
            if not cookie_file:
                raise Exception("No cookies found. Cannot download audio.")
                
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_file,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": False,
                # Added options for signature solving
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"]
                    }
                },
                # Other options
                "age_limit": 25,
                "ignoreerrors": True,
                # Modern user agent
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            cookie_file = cookie_txt_file(cookies_file)
            if not cookie_file:
                raise Exception("No cookies found. Cannot download video.")
                
            ydl_optssx = {
                "format": "bestvideo[height<=?720][width<=?1280]+bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_file,
                "no_warnings": True,
                "extract_flat": False,
                "skip_download": False,
                # Added options for signature solving
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"]
                    }
                },
                # Other options
                "age_limit": 25,
                "ignoreerrors": True,
                # Modern user agent
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            cookie_file = cookie_txt_file(cookies_file)
            if not cookie_file:
                raise Exception("No cookies found. Cannot download song video.")
                
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
                "extract_flat": False,
                "skip_download": False,
                # Added options for signature solving
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"]
                    }
                },
                # Other options
                "age_limit": 25,
                "ignoreerrors": True,
                # Modern user agent
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        def song_audio_dl():
            cookie_file = cookie_txt_file(cookies_file)
            if not cookie_file:
                raise Exception("No cookies found. Cannot download song audio.")
                
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_file,
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "extract_flat": False,
                "skip_download": False,
                # Added options for signature solving
                "extractor_args": {
                    "youtube": {
                        "player_client": ["android", "web"]
                    }
                },
                # Other options
                "age_limit": 25,
                "ignoreerrors": True,
                # Modern user agent
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        if songvideo:
            downloaded_file = await download_song(link, cookies_file)
            if not downloaded_file:
                # Fallback to yt-dlp
                downloaded_file = await yt_dlp_download_audio(link, cookies_file)
            fpath = f"downloads/{link}.mp3" if downloaded_file else None
            return fpath
        elif songaudio:
            downloaded_file = await download_song(link, cookies_file)
            if not downloaded_file:
                # Fallback to yt-dlp
                downloaded_file = await yt_dlp_download_audio(link, cookies_file)
            fpath = f"downloads/{link}.mp3" if downloaded_file else None
            return fpath
        elif video:
            # Try video API first
            try:
                downloaded_file = await download_video(link, cookies_file)
                if downloaded_file:
                    direct = True
                    return downloaded_file, direct
            except Exception as e:
                print(f"Video API failed: {e}")
            
            # Fallback to cookies
            cookie_file = cookie_txt_file(cookies_file)
            if not cookie_file:
                print("No cookies found. Cannot download video.")
                return None, None
                
            if await is_on_off(1):
                direct = True
                downloaded_file = await download_song(link, cookies_file)
                if not downloaded_file:
                    # Fallback to yt-dlp audio
                    downloaded_file = await yt_dlp_download_audio(link, cookies_file)
            else:
                # Updated command with new options
                cmd = [
                    "yt-dlp",
                    "--cookies", cookie_file,
                    "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "--age-limit", "25",
                    "--geo-bypass",
                    "--ignore-errors",
                    "--no-check-certificate",
                    "--quiet",
                    "--extractor-args", "youtube:player_client=android,web",
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    link
                ]
                
                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = False
                else:
                   file_size = await check_file_size(link, cookies_file)
                   if not file_size:
                     print("None file Size")
                     return None, None
                   total_size_mb = file_size / (1024 * 1024)
                   if total_size_mb > 250:
                     print(f"File size {total_size_mb:.2f} MB exceeds the 100MB limit.")
                     return None, None
                   direct = True
                   downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            direct = True
            downloaded_file = await download_song(link, cookies_file)
            if not downloaded_file:
                # Fallback to yt-dlp audio
                downloaded_file = await yt_dlp_download_audio(link, cookies_file)
        return downloaded_file, direct