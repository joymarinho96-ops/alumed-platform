from urllib.parse import parse_qs, quote, urlsplit, urlunsplit

OLD_BUCKET = "alumed-storage"
NEW_BUCKET = "alumed-storage-br"

OLD_PREFIX = f"https://storage.googleapis.com/{OLD_BUCKET}/"
NEW_PREFIX = f"https://storage.googleapis.com/{NEW_BUCKET}/"


def normalize_gcs_url(url):
    if not url:
        return url

    normalized = str(url).strip()
    if not normalized:
        return normalized

    # Handle gs:// bucket links.
    if normalized == f"gs://{OLD_BUCKET}":
        return NEW_PREFIX
    if normalized.startswith(f"gs://{OLD_BUCKET}/"):
        return NEW_PREFIX + normalized[len(f"gs://{OLD_BUCKET}/"):]

    try:
        parsed = urlsplit(normalized)
    except Exception:
        parsed = None

    if parsed and parsed.scheme and parsed.netloc:
        netloc = parsed.netloc.lower()
        path = parsed.path or ""

        # Common public bucket links.
        if netloc in {"storage.googleapis.com", "storage.cloud.google.com"}:
            if path == f"/{OLD_BUCKET}":
                path = f"/{NEW_BUCKET}"
            elif path.startswith(f"/{OLD_BUCKET}/"):
                path = f"/{NEW_BUCKET}/" + path[len(f"/{OLD_BUCKET}/"):]

            # GCS API links: .../download/storage/v1/b/<bucket>/o/...
            path = path.replace(f"/b/{OLD_BUCKET}/", f"/b/{NEW_BUCKET}/", 1)

            return urlunsplit(("https", "storage.googleapis.com", path, parsed.query, parsed.fragment))

    # Fallback replacements for known legacy variants.
    old_prefixes = (
        f"https://storage.googleapis.com/{OLD_BUCKET}/",
        f"https://storage.googleapis.com/{OLD_BUCKET}",
        f"http://storage.googleapis.com/{OLD_BUCKET}/",
        f"http://storage.googleapis.com/{OLD_BUCKET}",
        f"https://storage.cloud.google.com/{OLD_BUCKET}/",
        f"https://storage.cloud.google.com/{OLD_BUCKET}",
        f"http://storage.cloud.google.com/{OLD_BUCKET}/",
        f"http://storage.cloud.google.com/{OLD_BUCKET}",
    )

    for old in old_prefixes:
        if normalized.startswith(old):
            suffix = normalized[len(old):].lstrip("/")
            return NEW_PREFIX + suffix

    return normalized


def get_youtube_video_id(url):
    if not url:
        return ""

    normalized = str(url).strip()
    try:
        parsed = urlsplit(normalized)
    except Exception:
        return ""

    netloc = parsed.netloc.lower().replace("www.", "")
    path_parts = [part for part in parsed.path.split("/") if part]

    if netloc == "youtu.be" and path_parts:
        return path_parts[0]

    if netloc.endswith("youtube.com"):
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [""])[0]
        if path_parts and path_parts[0] in {"embed", "shorts", "live"} and len(path_parts) > 1:
            return path_parts[1]

    return ""


def get_google_drive_file_id(url):
    if not url:
        return ""

    normalized = str(url).strip()
    try:
        parsed = urlsplit(normalized)
    except Exception:
        return ""

    netloc = parsed.netloc.lower()
    if "drive.google.com" not in netloc and "docs.google.com" not in netloc:
        return ""

    query_id = parse_qs(parsed.query).get("id", [""])[0]
    if query_id:
        return query_id

    path_parts = [part for part in parsed.path.split("/") if part]
    if "d" in path_parts:
        index = path_parts.index("d")
        if len(path_parts) > index + 1:
            return path_parts[index + 1]

    return ""


def build_google_drive_preview_url(file_id):
    if not file_id:
        return ""
    return f"https://drive.google.com/file/d/{quote(file_id)}/preview"


def build_video_source(url, provider="auto"):
    """
    Return normalized playback metadata for course videos.

    YouTube private videos still require the viewer's Google account to have
    permission from YouTube. Google Drive videos require file sharing that
    allows the current viewer or anyone with the link to preview the file.
    """
    if not url:
        return {}

    normalized = str(url).strip()
    selected_provider = provider or "auto"
    youtube_id = get_youtube_video_id(normalized)
    drive_id = get_google_drive_file_id(normalized)

    if selected_provider == "youtube" or (selected_provider == "auto" and youtube_id):
        if youtube_id:
            return {
                "url": f"https://www.youtube.com/watch?v={youtube_id}",
                "embed_url": f"https://www.youtube.com/embed/{youtube_id}",
                "provider": "youtube",
                "player": "videojs",
                "mime_type": "video/youtube",
            }

    if selected_provider == "google_drive" or (selected_provider == "auto" and drive_id):
        if drive_id:
            preview_url = build_google_drive_preview_url(drive_id)
            return {
                "url": preview_url,
                "embed_url": preview_url,
                "provider": "google_drive",
                "player": "iframe",
                "mime_type": "text/html",
            }

    gcs_url = normalize_gcs_url(normalized)
    mime_type = "video/mp4"
    lowered_path = urlsplit(gcs_url).path.lower()
    if lowered_path.endswith(".m3u8"):
        mime_type = "application/x-mpegURL"
    elif lowered_path.endswith(".webm"):
        mime_type = "video/webm"
    elif lowered_path.endswith(".ogg") or lowered_path.endswith(".ogv"):
        mime_type = "video/ogg"

    return {
        "url": gcs_url,
        "embed_url": gcs_url,
        "provider": "google_cloud",
        "player": "videojs",
        "mime_type": mime_type,
    }

