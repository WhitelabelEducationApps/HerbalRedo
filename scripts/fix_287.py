# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import sqlite3, requests
from io import BytesIO
from pathlib import Path
try:
    from PIL import Image; HAS_PIL = True
except: HAS_PIL = False

DB = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db")
DRAWABLE = Path(r"C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\res\drawable-nodpi")
HEADERS = {"User-Agent": "HerbalRedo/1.0"}

IMG_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/Typha-cattails-in-indiana.jpg/500px-Typha-cattails-in-indiana.jpg"

r = requests.get(IMG_URL, headers=HEADERS, timeout=20)
r.raise_for_status()
dest = DRAWABLE / "cattail.jpg"
if HAS_PIL:
    Image.open(BytesIO(r.content)).convert("RGB").save(dest, "JPEG", quality=85)
else:
    dest.write_bytes(r.content)
print(f"Saved cattail.jpg ({dest.stat().st_size} bytes)")

conn = sqlite3.connect(DB)
conn.text_factory = lambda b: b.decode("utf-8", errors="replace")
conn.execute("""
    UPDATE museum_item SET
        full_image_uri   = ?,
        paintingname_zh  = '香蒲',
        paintingname_ru  = 'Рогоз',
        paintingname_ja  = 'ガマ',
        paintingname_hi  = 'नरकट'
    WHERE id = 287
""", (IMG_URL,))
conn.commit()
conn.close()
print("DB updated: image + 4 name fields fixed")
