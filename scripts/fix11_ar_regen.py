#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix 11: Regenerate Category C broken AR descriptions via Ollama."""
import sqlite3, sys, io, json, urllib.request, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'
OLLAMA_URL = 'http://localhost:11434/api/generate'
MODEL = 'qwen3:8b-ctx16k'

PLANTS = [
    (6,  'Astragalus', 'Astragalus (الأستراغالوس) - جنس من البقوليات يضم آلاف الأنواع، يُستخدم في الطب الصيني التقليدي كمقوّي مناعي'),
    (12, 'Bitter orange (Citrus aurantium)', 'البرتقال المر (Citrus aurantium) - يُستخدم في الطب التقليدي وصناعة العطور، يحتوي على السينفرين'),
    (13, 'Black cohosh (Actaea racemosa)', 'الكوشو الأسود (Actaea racemosa) - نبات أمريكي شمالي يُستخدم لأعراض سن اليأس'),
    (22, 'Senna occidentalis (coffee senna)', 'سنا غربي (Senna occidentalis) - نبات استوائي يُستخدم كمسهل في الطب التقليدي'),
    (42, 'Guava (Psidium guajava)', 'الجوافة (Psidium guajava) - فاكهة استوائية ذات قيمة طبية عالية'),
    (43, 'Hawthorn (Crataegus)', 'الزعرور (Crataegus) - شجيرة شوكية تُستخدم لصحة القلب والأوعية الدموية'),
    (85, 'Angelica sinensis (dong quai)', 'انجليكا صينية / دونغ كواي (Angelica sinensis) - عشبة صينية تقليدية تُستخدم في طب المرأة'),
]

def ollama_generate(prompt, timeout=120):
    data = json.dumps({
        'model': MODEL,
        'prompt': prompt,
        'stream': False,
        'options': {'num_predict': 400, 'temperature': 0.3}
    }).encode('utf-8')
    req = urllib.request.Request(OLLAMA_URL, data=data,
                                  headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            text = result.get('response', '').strip()
            # Strip <think> blocks
            if '<think>' in text.lower():
                end = text.find('</think>')
                if end != -1:
                    text = text[end + 8:].strip()
            return text
    except Exception as e:
        return None

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()
updated = 0

for pid, plant_name, hint in PLANTS:
    print(f'Generating AR for id={pid} ({plant_name})...', flush=True)
    prompt = (
        f"اكتب وصفاً طبياً نباتياً باللغة العربية الفصحى لنبات: {plant_name}.\n"
        f"السياق: {hint}.\n"
        f"الوصف يجب أن يتضمن: الموطن الأصلي، الخصائص الطبية، المواد الفعالة، الاستخدامات التقليدية.\n"
        f"اكتب 4-5 جمل. لا تستخدم الأحرف الصينية أو اليابانية. باللغة العربية فقط."
    )
    text = ollama_generate(prompt)
    if text:
        cur.execute('UPDATE museum_item SET description_ar=? WHERE id=?', (text, pid))
        updated += 1
        print(f'  Done ({len(text)} chars)')
    else:
        print(f'  FAILED for id={pid}')
    time.sleep(1)

conn.commit()
print(f'\nAR descriptions updated: {updated}')
conn.close()
