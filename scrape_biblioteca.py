
from bs4 import BeautifulSoup
import re, json

with open("conecta-biblioteca-source.html", "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

results = {
    "download_wixmp_links": [],
    "drive_links": [],
    "all_links_with_text": [],
    "json_fileUrls": [],
    "json_fileNames": []
}

# 1. Links de download-files.wixmp.com (PDFs reales)
wixmp = re.findall(r'https?://download-files\.wixmp\.com/raw/[^\s"\'<>]+', html)
results["download_wixmp_links"] = list(set(wixmp))

# 2. Links de Google Drive
drive = re.findall(r'https?://drive\.google\.com/[^\s"\'<>]+', html)
results["drive_links"] = list(set(drive))

# 3. Todos los <a href> con texto
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = a.get_text(strip=True)
    if href and href.startswith("http") and len(text) > 2:
        results["all_links_with_text"].append({"text": text[:80], "url": href})

# 4. fileUrl en JSON/scripts
file_urls = re.findall(r'"fileUrl"\s*:\s*"([^"]+)"', html)
results["json_fileUrls"] = list(set(file_urls))

# 5. displayName/fileName en JSON
file_names_json = re.findall(r'"displayName"\s*:\s*"([^"]+)"', html)
results["json_fileNames"] = list(set(file_names_json))

# 6. Buscar patron de archivo en JSON (nombre + url juntos)
# Formato: {"displayName":"xxx","...","url":"yyy"}
combined = re.findall(r'"displayName"\s*:\s*"([^"]+)"[^}]*"fileUrl"\s*:\s*"([^"]+)"', html)

print(f"download-files.wixmp.com links: {len(results['download_wixmp_links'])}")
print(f"Google Drive links: {len(results['drive_links'])}")
print(f"Links con texto en <a>: {len(results['all_links_with_text'])}")
print(f"fileUrl en JSON: {len(results['json_fileUrls'])}")
print(f"displayName en JSON: {len(results['json_fileNames'])}")
print(f"Combined (nombre+url): {len(combined)}")

print("\n=== WIXMP LINKS ===")
for l in results["download_wixmp_links"][:20]:
    print(l[:100])

print("\n=== DRIVE LINKS ===")
for l in results["drive_links"][:10]:
    print(l[:100])

print("\n=== FILE NAMES FROM JSON ===")
for n in results["json_fileNames"][:30]:
    print(n)

print("\n=== COMBINED (nombre+url) ===")
for name, url in combined[:20]:
    print(f"{name[:60]} -> {url[:80]}")

# Guardar resultados completos
with open("biblioteca_links_scraped.json", "w", encoding="utf-8") as f:
    json.dump({
        "wixmp": results["download_wixmp_links"],
        "drive": results["drive_links"],
        "fileNames": results["json_fileNames"],
        "combined": [{"name": n, "url": u} for n,u in combined]
    }, f, ensure_ascii=False, indent=2)

print("\nResultados guardados en biblioteca_links_scraped.json")
