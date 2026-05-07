import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from email.utils import formatdate
from datetime import datetime, timezone
from hashlib import md5

NEWS_URL = "https://tvn24.pl/polska"
OUTPUT_FILE = "tvn24polska.xml"

# Download page
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

# Parse HTML
soup = BeautifulSoup(response.text, "lxml")

# Create RSS feed
fg = FeedGenerator()

fg.title("TVN24 Polska")
fg.link(href=NEWS_URL, rel="alternate")
fg.description("Auto-generated TVN24 Polska RSS feed")
fg.language("pl")

# Find article headline links
articles = soup.select("a.sc-kMkxajy.hLjhzTy")

seen = set()
added = 0

for article in articles:

    title = article.get("title", "").strip()
    link = article.get("href", "").strip()

    if not title or not link:
        continue

    # Skip duplicates
    if link in seen:
        continue

    seen.add(link)

    # Keep only Poland news articles
    if "/polska/" not in link:
        continue

    # Create stable GUID
    guid = md5(link.encode("utf-8")).hexdigest()

    # Create feed entry
    fe = fg.add_entry()

    fe.title(title)
    fe.link(href=link)
    fe.guid(guid)

    # Simple description
    fe.description(title)

    # Optional:
    # If real publication dates are later discovered,
    # replace this with parsed article timestamps.

    added += 1

# Debug output
print(f"Articles added: {added}")

# Write RSS XML
fg.rss_file(OUTPUT_FILE)

print(f"RSS feed generated successfully: {OUTPUT_FILE}")
