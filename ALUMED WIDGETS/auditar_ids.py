import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

with open("app.js", "r", encoding="utf-8") as f:
    app_js = f.read()

html_ids = set(re.findall(r'id=["\']([^"\']+)["\']', html))
app_ids = set(re.findall(r'getElementById\(["\']([^"\']+)["\']\)', app_js))

missing = []
for aid in app_ids:
    if aid not in html_ids:
        missing.append(aid)

print(f"Total IDs en index.html: {len(html_ids)}")
print(f"Total getElementById en app.js: {len(app_ids)}")
print("\n--- IDs USADOS EN APP.JS QUE NO EXISTEN EN INDEX.HTML ---")
for m in missing:
    print(f" [MISSING] {m}")
