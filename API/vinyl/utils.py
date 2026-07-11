import json
import urllib.error
import urllib.parse
import urllib.request

ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


def fetch_album_cover(title, artist, timeout=3):
    """Looks up an album on the iTunes Search API and returns a 600x600
    artwork URL, or None if nothing was found or the request failed."""
    if not title or not artist:
        return None

    query = urllib.parse.urlencode({
        'term': f"{title} {artist}",
        'media': 'music',
        'entity': 'album',
        'limit': 5,
    })
    url = f"{ITUNES_SEARCH_URL}?{query}"

    try:
        request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return None

    results = data.get('results') or []
    if not results:
        return None

    artwork_url = results[0].get('artworkUrl100')
    if not artwork_url:
        return None

    return artwork_url.replace('100x100bb', '600x600bb')
