import os

try:
    import yt_dlp
except Exception:  # pragma: no cover - optional dependency in deployment
    yt_dlp = None

try:
    from pydub import AudioSegment
except Exception:  # pragma: no cover - optional dependency in deployment
    AudioSegment = None

DOWNLOAD_DIR = 'downloades'
os.makedirs(DOWNLOAD_DIR,exist_ok = True)


def _build_youtube_dl_options(output_path: str) -> dict:
    return {
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
        "retries": 2,
        "socket_timeout": 30,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["web_embedded", "android", "web"],
                "player_skip": ["configs", "webplayer"],
            }
        },
    }


def download_youtube_audio(url: str) -> str:
    if yt_dlp is None:
        raise RuntimeError("yt-dlp is not installed. Please install requirements first.")

    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    attempts = [
        _build_youtube_dl_options(output_path),
        {
            **_build_youtube_dl_options(output_path),
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "web_embedded"],
                    "player_skip": ["configs", "webplayer"],
                }
            },
        },
    ]

    last_error: Exception | None = None

    for attempt in attempts:
        try:
            with yt_dlp.YoutubeDL(attempt) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    raise RuntimeError("The video metadata could not be retrieved.")
                filename = ydl.prepare_filename(info)
        except Exception as exc:
            last_error = exc
            continue

        return filename.replace(".webm", ".wav").replace(".m4a", ".wav")

    raise RuntimeError(
        "Unable to download the YouTube audio. The URL may be private, blocked, or temporarily unavailable. Please try a different URL or use a local file instead."
    ) from last_error



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    if AudioSegment is None:
        raise RuntimeError("pydub is not installed. Please install requirements first.")

    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000) #16khz
    audio.export(output_path, format="wav")
    return output_path



def chunk_audio(wav_path : str , chunk_minutes : int = 10) -> list:
    if AudioSegment is None:
        raise RuntimeError("pydub is not installed. Please install requirements first.")

    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000 

    chunks = []

    for i, start in enumerate(range(0,len(audio),chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path , format = "wav")

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

