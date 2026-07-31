import os

try:
    import yt_dlp
except Exception:
    yt_dlp = None

try:
    from pydub import AudioSegment
except Exception:
    AudioSegment = None

try:
    from curl_cffi import requests as _curl_requests
    _HAS_CURL_CFFI = True
except Exception:
    _HAS_CURL_CFFI = False

try:
    from yt_dlp.networking.impersonate import ImpersonateTarget

    def _impersonate_target(name: str = "chrome"):
        try:
            return ImpersonateTarget.parse_from_str(name)
        except Exception:
            return ImpersonateTarget(name)
except Exception:
    def _impersonate_target(name: str = "chrome"):
        return name

DOWNLOAD_DIR = 'downloads'
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def _build_youtube_dl_options(output_path: str, attempt: int = 0) -> dict:
    base = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "retries": 5,
        "fragment_retries": 5,
        "file_access_retries": 5,
        "extractor_retries": 5,
        "socket_timeout": 60,
        "ignoreerrors": False,
        **({"impersonate": _impersonate_target("chrome")} if _HAS_CURL_CFFI else {}),
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Origin": "https://www.youtube.com",
            "Referer": "https://www.youtube.com/",
        },
    }

    if attempt == 0:
        base["extractor_args"] = {
            "youtube": {
                "player_client": ["web_embedded", "android", "web"],
                "player_skip": ["configs", "webplayer", "js"],
            }
        }
    elif attempt == 1:
        base["extractor_args"] = {
            "youtube": {
                "player_client": ["android", "web_embedded", "ios"],
                "player_skip": ["configs", "webplayer", "js"],
            }
        }
    elif attempt == 2:
        base["extractor_args"] = {
            "youtube": {
                "player_client": ["web_embedded", "android"],
                "player_skip": ["configs", "webplayer", "js"],
            }
        }
        base["impersonate"] = _impersonate_target("chrome")
        for cookie_path in [
            os.path.expanduser("~/.config/yt-dlp/cookies.txt"),
            os.path.expanduser("~/.cache/yt-dlp/cookies.txt"),
            "cookies.txt",
        ]:
            if os.path.exists(cookie_path):
                base["cookiefile"] = cookie_path
                break
    elif attempt == 3:
        base["extractor_args"] = {
            "youtube": {
                "player_client": ["tv_embedded", "tv"],
                "player_skip": ["configs", "webplayer", "js"],
            }
        }
        base["impersonate"] = _impersonate_target("chrome")

    return base


def download_youtube_audio(url: str) -> str:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed. Please install requirements first.")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    max_attempts = 4
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            opts = _build_youtube_dl_options(output_path, attempt)
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise RuntimeError("The video metadata could not be retrieved.")
                filename = ydl.prepare_filename(info)
                wav_path = os.path.splitext(filename)[0] + ".wav"
        except Exception as exc:
            last_error = exc
            print(f"  ⚠️ yt-dlp attempt {attempt + 1}/{max_attempts} failed: {exc}")
            continue

        if os.path.exists(wav_path):
            return wav_path
        return filename

    raise RuntimeError(
        "Unable to download the YouTube audio after multiple attempts. "
        "The video may be private, age-restricted, region-blocked, or YouTube has "
        "temporarily throttled downloads. Please try:\n"
        "- A different video URL\n"
        "- Using a local file instead\n"
        "- Installing a JavaScript runtime: `pip install yt-dlp[default]` or `npm install -g jsdom`\n"
        "  (see https://github.com/yt-dlp/yt-dlp/wiki/EJS for details)"
    ) from last_error


def convert_to_wav(input_path: str) -> str:
    if AudioSegment is None:
        raise RuntimeError("pydub is not installed. Please install requirements first.")

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    if AudioSegment is None:
        raise RuntimeError("pydub is not installed. Please install requirements first.")

    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks

