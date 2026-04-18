"""
MindMetrics build script — inlines Google Fonts into index.html
Outputs a fully self-contained dist/index.html with no external dependencies.
"""

import os, re, base64, urllib.request

FONTS_URL = (
    "https://fonts.googleapis.com/css2?"
    "family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;0,700;1,300;1,400"
    "&family=Space+Mono:wght@400;700"
    "&family=Jost:wght@300;400;500;600"
    "&display=swap"
)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36"

def fetch(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

# 1. Fetch Google Fonts CSS (request woff2 via Chrome UA)
print("Fetching Google Fonts CSS...")
css_bytes = fetch(FONTS_URL, {"User-Agent": UA})
css = css_bytes.decode("utf-8")

# 2. Download each font file and replace with base64 data URI
font_urls = re.findall(r'url\((https://fonts\.gstatic\.com/[^)]+)\)', css)
print(f"Found {len(font_urls)} font files to embed...")

for font_url in font_urls:
    print(f"  Embedding: {font_url.split('/')[-1]}")
    font_data = fetch(font_url, {"User-Agent": UA})
    b64 = base64.b64encode(font_data).decode("ascii")
    data_uri = f"data:font/woff2;base64,{b64}"
    css = css.replace(font_url, data_uri)

# 3. Read source HTML
with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 4. Replace the <link> Google Fonts tag with an inline <style> block
link_pattern = re.compile(
    r'<link\s[^>]*fonts\.googleapis\.com[^>]*>',
    re.IGNORECASE | re.DOTALL
)
# Also remove the preconnect hints for Google Fonts
preconnect_pattern = re.compile(
    r'<link\s[^>]*preconnect[^>]*googleapis[^>]*>\s*',
    re.IGNORECASE | re.DOTALL
)
html = preconnect_pattern.sub('', html)
html = link_pattern.sub(f'<style>\n/* Google Fonts — inlined for offline use */\n{css}\n</style>', html)

# 5. Write output
os.makedirs("dist", exist_ok=True)
out_path = os.path.join("dist", "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

size_kb = os.path.getsize(out_path) // 1024
print(f"\nBuild complete: dist/index.html ({size_kb} KB) — fully self-contained.")
