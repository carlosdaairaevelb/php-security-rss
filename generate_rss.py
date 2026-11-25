"""Genera docs/feed.xml con los avisos de seguridad publicados de php/php-src."""

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.etree.ElementTree import Element, ElementTree, SubElement

# Los N avisos más recientes por fecha de publicación. Power Automate solo
# necesita los nuevos; limitarlos evita perder avisos al superar una página
# de la API y mantiene el feed ligero.
MAX_ITEMS = 30
SUMMARY_MAX_CHARS = 500

URL = (
    "https://api.github.com/repos/php/php-src/security-advisories"
    f"?state=published&sort=published&direction=desc&per_page={MAX_ITEMS}"
)
SEVERITY_LABELS = {
    "critical": "CRÍTICA",
    "high": "ALTA",
    "medium": "MEDIA",
    "low": "BAJA",
}

headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "php-security-rss",
}
token = os.environ.get("GITHUB_TOKEN")
if token:
    headers["Authorization"] = f"Bearer {token}"


def fetch_advisories():
    request = urllib.request.Request(URL, headers=headers)
    for attempt in range(1, 4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except (urllib.error.URLError, TimeoutError) as error:
            if attempt == 3:
                raise
            print(f"Intento {attempt} fallido ({error}); reintentando...")
            time.sleep(10 * attempt)


def plain_summary(markdown):
    """Primer párrafo de la sección «Summary» (o del texto), sin Markdown."""
    text = (markdown or "").replace("\r\n", "\n")
    match = re.search(r"#+\s*Summary\s*\n+(.+?)(?:\n\s*\n|\n#|$)", text, re.S | re.I)
    paragraph = match.group(1) if match else text.strip().split("\n\n")[0]
    # Quita marcas de Markdown sin tocar los "_" de nombres como php_foo_bar.
    paragraph = re.sub(r"[`*#>]|(?<!\w)_+|_+(?!\w)", "", paragraph)
    paragraph = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", paragraph)
    paragraph = " ".join(paragraph.split())
    if len(paragraph) > SUMMARY_MAX_CHARS:
        paragraph = paragraph[:SUMMARY_MAX_CHARS].rsplit(" ", 1)[0] + "…"
    return paragraph


def cvss_score(advisory):
    severities = advisory.get("cvss_severities") or {}
    for key in ("cvss_v4", "cvss_v3"):
        score = (severities.get(key) or {}).get("score")
        if score:
            return f"{score} ({key.replace('cvss_v', 'CVSS v')})"
    score = (advisory.get("cvss") or {}).get("score")
    return str(score) if score else None


def details(advisory):
    severity = (advisory.get("severity") or "").lower()
    lines = [f"Gravedad: {SEVERITY_LABELS.get(severity, severity.upper() or 'N/D')}"]
    score = cvss_score(advisory)
    if score:
        lines.append(f"CVSS: {score}")
    if advisory.get("cve_id"):
        lines.append(f"CVE: {advisory['cve_id']}")
    vulns = advisory.get("vulnerabilities") or []
    components = sorted({v["package"]["name"] for v in vulns if v.get("package")})
    if components:
        lines.append(f"Componente: {', '.join(components)}")
    patched = [v["patched_versions"] for v in vulns if v.get("patched_versions")]
    if patched:
        lines.append(f"Versiones corregidas: {', '.join(dict.fromkeys(patched))}")
    return lines, components


advisories = fetch_advisories()

rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")
SubElement(channel, "title").text = "PHP Security Advisories"
SubElement(channel, "link").text = "https://github.com/php/php-src/security/advisories"
SubElement(channel, "description").text = "Avisos oficiales de seguridad PHP"
SubElement(channel, "language").text = "es"
SubElement(channel, "lastBuildDate").text = format_datetime(datetime.now(timezone.utc))
SubElement(channel, "ttl").text = "720"

for advisory in advisories:
    severity = (advisory.get("severity") or "").lower()
    label = SEVERITY_LABELS.get(severity, severity.upper() or "N/D")
    lines, components = details(advisory)
    summary = plain_summary(advisory.get("description"))

    item = SubElement(channel, "item")
    SubElement(item, "title").text = f"[{label}] {advisory['summary']}"
    SubElement(item, "link").text = advisory["html_url"]
    SubElement(item, "guid", isPermaLink="false").text = advisory["ghsa_id"]
    SubElement(item, "description").text = "\n".join(lines + ["", summary]).strip()
    # Categorías: Power Automate las expone en el disparador RSS y sirven
    # para filtrar o dar formato según la gravedad.
    if severity:
        SubElement(item, "category").text = severity
    for component in components:
        SubElement(item, "category").text = component
    published = advisory.get("published_at")
    if published:
        dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
        SubElement(item, "pubDate").text = format_datetime(dt)

os.makedirs("docs", exist_ok=True)
ElementTree(rss).write("docs/feed.xml", encoding="utf-8", xml_declaration=True)
print(f"Feed generado con {len(advisories)} avisos.")
