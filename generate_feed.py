import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from hashlib import md5
from urllib.parse import urljoin
from email.utils import formatdate
import time

NEWS_URL = "https://tvn24.pl/polska"
OUTPUT_FILE = "tvn24polska.rss"

# -----------------------------
# Download page (safe encoding)
# -----------------------------
response = requests.get(
    NEWS_URL,
    headers={
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    },
    timeout=30
)

response.raise_for_status()

# Force correct encoding for Polish characters
response.encoding = response.apparent_encoding or "utf-8"
html = response.content.decode(response.encoding, errors="replace")

# -----------------------------
# Parse HTML
# -----------------------------
soup = BeautifulSoup(html, "lxml")

# -----------------------------
# Create RSS feed
# -----------------------------
fg = FeedGenerator()

fg.title("TVN24 Polska")
fg.link(href=NEWS_URL, rel="alternate")
fg.description("Auto-generated TVN24 Polska RSS feed")
fg.language("pl")

# -----------------------------
# Extract articles
# -----------------------------
articles = soup.select("a.sc-kMkxajy.hLjhzTy")

seen = set()
added = 0

for article in articles:

    title = article.get("title", "").strip()
    link = article.get("href", "").strip()

    if not title or not link:
        continue

    # Convert to absolute URL (fix for RSS readers)
    link = urljoin(NEWS_URL, link)

    if link in seen:
        continue
    seen.add(link)

    if "/polska/" not in link:
        continue

    # Stable GUID
    guid = md5(link.encode("utf-8")).hexdigest()

    fe = fg.add_entry()
    fe.title(title)
    fe.link(href=link)

    # GUID explicitly marked as non-permalink
    fe.guid(guid, permalink=False)

    fe.description(title)

    # Required for stricter RSS readers (ustart fix)
    fe.pubDate(formatdate(time.time(), usegmt=True))

    added += 1

print(f"Articles added: {added}")

# -----------------------------
# Write RSS (strict UTF-8)
# -----------------------------
rss_feed = fg.rss_str(pretty=True, encoding="utf-8", xml_declaration=True)

if isinstance(rss_feed, bytes):
    rss_feed = rss_feed.decode("utf-8")

with open(OUTPUT_FILE, "w", encoding="utf-8", newline="\n") as f:
    f.write(rss_feed)

print(f"RSS feed generated successfully: {OUTPUT_FILE}")
