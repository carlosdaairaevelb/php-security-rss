
import json
import os
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

URL = "https://api.github.com/repos/php/php-src/security-advisories?state=published&per_page=100"
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "php-security-rss"
}
token = os.environ.get("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"

request = urllib.request.Request(URL, headers=headers)
with urllib.request.urlopen(request, timeout=30) as response:
    advisories = json.load(response)

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "PHP Security Advisories"
SubElement(channel, "link").text = "https://github.com/php/php-src/security/advisories"
SubElement(channel, "description").text = "Avisos oficiales de seguridad PHP"

for advisory in advisories:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = advisory["summary"]
    SubElement(item, "link").text = advisory["html_url"]
    SubElement(item, "guid", isPermaLink="false").text = advisory["ghsa_id"]
    SubElement(item, "description").text = advisory.get("description") or ""
    published = advisory.get("published_at")
    if published:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        SubElement(item, "pubDate").text = format_datetime(dt)

os.makedirs("docs", exist_ok=True)
ElementTree(rss).write("docs/feed.xml", encoding="utf-8", xml_declaration=True)
