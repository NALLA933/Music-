import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", "35660683"))
API_HASH = getenv("API_HASH", "7afb42cd73fb5f3501062ffa6a1f87f7")

# Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN", "8504453753:AAFD5zuyYvOmAWLzXlczzUFeHouW6nxh0JM")

# Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://hnyx:wywyw2@cluster0.9dxlslv.mongodb.net/?retryWrites=true&w=majority")

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "60"))

# Chat id of a group for logging bot's activities
LOG_GROUP_ID = int(getenv("LOG_GROUP_ID", "-1002059929123"))

# Get this value from @MissRose_Bot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "7818323042"))

## Fill these variables if you're deploying on heroku.
# Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
# Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

API_URL = getenv("API_URL", "https://api.nexgenbots.xyz") #youtube song url
VIDEO_API_URL = getenv("VIDEO_API_URL", "https://api.video.nexgenbots.xyz")
API_KEY = getenv("API_KEY", "30DxNexGenBots3a3e08") # youtube song api key, generate free key or buy paid plan from panel.thequickearn.xyz

# YouTube cookies for bypassing restrictions (can be a file path or cookie string)
YOUTUBE_COOKIES = getenv("YOUTUBE_COOKIES", """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1784803915	__Secure-YNID	15.YT=GMc8Q7nB9EB71dHCr8cg5EW55tb2tF0qBOYuYVsSWTRKc60MBfP8iAOuD1e4TblSqirLHbC1_ZLiSm8AmXvoToCr7Fs6fwERfnizoz17uwU9XzhvpT22Ca1XYak5jURjUYNuNVF4Od_KNXY8OaaPIAXTwYmzsuawleDCxkwfN3nvLmFt7U-vlkf0wffXfwC_-81DkBP7G30agKd2QxY_3nPp1mZp1qatMDyAJ341uWEBObg3rZJ1dv6cAFCyXjnxK_R1QmEiSCCsOGvapV63mRducBQJaf1aVmH4l7XtDyRMsSwAQNAVVWcJ9WJ9Z5UxH0eiqhbQwLnUqiBrhZnMng
.youtube.com	TRUE	/	TRUE	1769253715	GPS	1
.youtube.com	TRUE	/	TRUE	0	YSC	bzDCQUsKyV8
.youtube.com	TRUE	/	TRUE	1784804005	VISITOR_INFO1_LIVE	QlBDPtF9EQI
.youtube.com	TRUE	/	TRUE	1784804005	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgNg%3D%3D
.youtube.com	TRUE	/	TRUE	1803812007	PREF	f6=40000000&tz=Asia.Kolkata
.youtube.com	TRUE	/	TRUE	1800788002	__Secure-1PSIDTS	sidts-CjUB7I_69AqtnP1OfWKJWguTe3nvkbA8omcwrB4WSI4bJZpue16aIL7Jtnqoco9uFcTe44JSQhAA
.youtube.com	TRUE	/	TRUE	1800788002	__Secure-3PSIDTS	sidts-CjUB7I_69AqtnP1OfWKJWguTe3nvkbA8omcwrB4WSI4bJZpue16aIL7Jtnqoco9uFcTe44JSQhAA
.youtube.com	TRUE	/	FALSE	1803812007	HSID	AAcS_yaccTtSThpxc
.youtube.com	TRUE	/	TRUE	1803812007	SSID	AsEwcUF7QUvTrUWDx
.youtube.com	TRUE	/	FALSE	1803812007	APISID	eM9I2QdzdroqRIp1/AlnSQGsYR_9WPE8q-
.youtube.com	TRUE	/	TRUE	1803812007	SAPISID	JGFUrj2MNYUevZa9/ATq-P46uK0UjRAjrf
.youtube.com	TRUE	/	TRUE	1803812007	__Secure-1PAPISID	JGFUrj2MNYUevZa9/ATq-P46uK0UjRAjrf
.youtube.com	TRUE	/	TRUE	1803812007	__Secure-3PAPISID	JGFUrj2MNYUevZa9/ATq-P46uK0UjRAjrf
.youtube.com	TRUE	/	FALSE	1803812007	SID	g.a0006AiAwBPYp8WmWzz13e8dxM3ZNVDOWgKOirwaJ_ljjGI4SVFTwzpx-IjAyNYkmY2PrU_rqQACgYKAYcSARcSFQHGX2Mirak5OnbfAlg79YniZwrjFxoVAUF8yKq4YPwCZlsgNQYdDBWP6_Ap0076
.youtube.com	TRUE	/	TRUE	1803812007	__Secure-1PSID	g.a0006AiAwBPYp8WmWzz13e8dxM3ZNVDOWgKOirwaJ_ljjGI4SVFT2jdquc0Gy1h5-sr2rxvUpgACgYKAdESARcSFQHGX2MiIx4e2SdHOL51Wh7NuKFD7BoVAUF8yKrSvE48Iv6PDzUA-bNEg-u70076
.youtube.com	TRUE	/	TRUE	1803812007	__Secure-3PSID	g.a0006AiAwBPYp8WmWzz13e8dxM3ZNVDOWgKOirwaJ_ljjGI4SVFT4SaPF8JWlCbKcP5Pf6XR0gACgYKAd0SARcSFQHGX2MiwgeNO1-TgQW-domr0rwnCRoVAUF8yKq54A31s5HbPQ1xS_Dd6t6y0076
.youtube.com	TRUE	/	TRUE	1803812004	LOGIN_INFO	AFmmF2swRQIhAMIEHtaYSpgQnT1qsDGw3y8EL6rqEOPkmKgc0RDSCzJ3AiBjNcrHkY3Rrxu0BKQFPlO1Qe-iPnnBzyD63ipBlqZnjA:QUQ3MjNmejlpSGNzZ0Njbk1ZY3RNRFRmSnhkdDZIMzdsdlpnLXViQlg0bk9lemNyTFN2WER5SWxxbXdFeXQzWkoyMmVvZDd6Uy0yM1dvTWowZkpKT083blAtTnJnbEtJMmI1RVUwSkp0eVNTMnpLNnh6dU56bmlaeVNJeE1SMWE4aHZyR0FZbWxRYXFYOWFlZjRSa2dWb0VLMERlYXp3MHJ3
.youtube.com	TRUE	/	TRUE	1769252124	YTSESSION-sobm4z	ANPz9KhyZ5eBd/CG1Keqm7of9DGnCN24DZLvi3gHa8l9BiainJulCb7CW1SVFTRuAU552awVJgj8lPjude/bQWEdadxLKV+FEl9q6Pk=
.youtube.com	TRUE	/	FALSE	1800788009	SIDCC	AKEyXzXLouadpYXF9ZPWByRFHMwXtnEwYBkl0ayOSEykAJTwlSao0Gvfa3PWO-NvZ4Wm-er7Xg
.youtube.com	TRUE	/	TRUE	1800788009	__Secure-1PSIDCC	AKEyXzVUcu2b2PHgBpQV5dnuB3266C6yHEmPWLPcic3_DFfEDImvpPDGxGq-rfgvjA692tUjxA
.youtube.com	TRUE	/	TRUE	1800788009	__Secure-3PSIDCC	AKEyXzUa7hjAEOFOJqERQFSFQcZZcUEGwodVVVgFhOyA95KmyAK0lvNFCTicNIlbWy7p4km7
.youtube.com	TRUE	/	TRUE	1769252124	YTSESSION-js1wlf	ANPz9KiUIn5vh8d2D0jPdWmWjlgCxVquNOPAsXIXD2SIXqX8p6CbnecrdC4QS2mh9aglNuK2gtjtZnvQFZzPWl25mNWI6WmO/FoPogo=
.youtube.com	TRUE	/	FALSE	1769252011	ST-l3hjtt	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252011	ST-tladcw	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252016	ST-3opvp5	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252013	ST-uwicob	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252013	ST-xuwub9	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252019	ST-1b	csn=jToAZ-hNnKAoMnJA&itct=CCIQ8KgHGAAiEwiZ15jpgqSSAxVEwDgGHa-SHBXKAQSorJD_&endpoint=%7B%22clickTrackingParams%22%3A%22CCIQ8KgHGAAiEwiZ15jpgqSSAxVEwDgGHa-SHBXKAQSorJD_%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2F%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_BROWSE%22%2C%22rootVe%22%3A3854%2C%22apiUrl%22%3A%22%2Fyoutubei%2Fv1%2Fbrowse%22%7D%7D%2C%22browseEndpoint%22%3A%7B%22browseId%22%3A%22FEwhat_to_watch%22%7D%7D&session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252018	ST-yve142	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252019	ST-hcbf8d	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
.youtube.com	TRUE	/	FALSE	1769252059	ST-sobm4z	gs_l=youtube.12.....0.48893......0......ytlcmt5_e2%2Crlmn%3Dmanual_model_longclick_v2_vizier_tune_10_20251223_ast_proto-recordio.0...............&oq=tu%20hai%20kha&itct=CBMQ7VAiEwjM8ufsgqSSAxWoyhYFHTCvJpvKAQSorJD_&csn=Yw-je-cFnYsG8WVv&session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB&endpoint=%7B%22clickTrackingParams%22%3A%22CBMQ7VAiEwjM8ufsgqSSAxWoyhYFHTCvJpvKAQSorJD_%22%2C%22commandMetadata%22%3A%7B%22webCommandMetadata%22%3A%7B%22url%22%3A%22%2Fresults%3Fsearch_query%3Dtu%2Bhai%2Bkha%22%2C%22webPageType%22%3A%22WEB_PAGE_TYPE_SEARCH%22%2C%22rootVe%22%3A4724%7D%7D%2C%22searchEndpoint%22%3A%7B%22query%22%3A%22tu%20hai%20kha%22%7D%7D
.youtube.com	TRUE	/	FALSE	1769252059	ST-1k06sw0	session_logininfo=AFmmF2swRgIhAO8VTU4Ha055pSg-u5mITRMeGezu-4sgrYRpdQUbhyraAiEAg3PNdsGVn9qgpQqgHUwzcVPukCmEF6U1bhx_skbcpx4%3AQUQ3MjNmeGloZHVUVVJpamZMbm1vTmhseWlCcXdRSHptSElZcnJsanlfa2NzQ1p6aEt6UnpLUDZzX2RWNURjdTEwZXVwU3JweVJHMXQxZ1hIRDlrRGU5TXBIWjYtQzF1QzFhWmxJOGp4MEFDQUUta1htMWo5TUM5R2FseHF3SFZYOWt3Y1NZNTd1aXpnVTFkR04yeUpMQl9zZ2Y5dlZ3NzZB
""")

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/NALLA933/Music-",
)
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  # Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/PICK_X_UPDATE")
SUPPORT_GROUP = getenv("SUPPORT_GROUP", "https://t.me/THE_DRAGON_SUPPORT")

# Set this to True if you want the assistant to automatically leave chats after an interval
AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))

# make your bots privacy from telegra.ph and put your url here 
PRIVACY_LINK = getenv("PRIVACY_LINK", "https://telegra.ph/Privacy-Policy-for-AviaxMusic-08-14")


# Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)


# Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))


# Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "104857600"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "2145386496"))
# Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes


# Get your pyrogram v2 session from Replit
STRING1 = getenv("STRING_SESSION", "BQITRnsAeRimAnwhsD7Y7rg0dcWJFZev70hyKiwMavyzb7lyg8ANRWySDAItUHYiLbjB1GkFtXtJce-cC20ZmusRb5tsObEZm2aysX9S3YU46PCGxyhWSY6iib_XqffTce5vJDk6J81PDJiHXns3OSa9IuX9evfIIo77_MNLE3eWd6i-RsyqI61Zw62x4i2N8H2Y37G-oqYB1ypIOYOIo5yeZc-DsveSS89rg18T43qOrDLX7O4UJHo5xcvpSTpYU27rGlx5PaF8jH4IChdYmxCwhk6BtQjALboXrktGksIlib2mS1uZie4FiQW3XUNM5x8iRoqc1oSPuJnFuU1n9d8lE_r9GAAAAAH1bYMHAA")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)


BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://files.catbox.moe/t0hoy3.mp4"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://graph.org//file/389a372e8ae039320ca6c.png"
)
PLAYLIST_IMG_URL = "https://graph.org//file/3dfcffd0c218ead96b102.png"
STATS_IMG_URL = "https://files.catbox.moe/6rnc92.jpg"
TELEGRAM_AUDIO_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
TELEGRAM_VIDEO_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
STREAM_IMG_URL = "https://te.legra.ph/file/bd995b032b6bd263e2cc9.jpg"
SOUNCLOUD_IMG_URL = "https://te.legra.ph/file/bb0ff85f2dd44070ea519.jpg"
YOUTUBE_IMG_URL = "https://graph.org//file/2f7debf856695e0ef0607.png"
SPOTIFY_ARTIST_IMG_URL = "https://te.legra.ph/file/37d163a2f75e0d3b403d6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://te.legra.ph/file/b35fd1dfca73b950b1b05.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://te.legra.ph/file/95b3ca7993bbfaf993dcb.jpg"


def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_GROUP:
    if not re.match("(?:http|https)://", SUPPORT_GROUP):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_GROUP url is wrong. Please ensure that it starts with https://"
        )