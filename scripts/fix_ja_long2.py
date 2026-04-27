#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3

DB_PATH = r'C:\Users\rsavu\AndroidStudioProjects\HerbalRedo\androidApp\src\main\assets\plants.db'

JA_FIXES2 = {
    26:  'ジギタリス・ラナータ',
    33:  'フェヌグリーク',
    43:  'セイヨウサンザシ',
    46:  'スギナ',
    47:  'ジャマイカドッグウッド',
    85:  '当帰',
    216: 'スカエボラ',
    228: 'ウスベニタチアオイ',
    230: 'メラストマ',
    270: 'ドクダミ',
    273: 'モウズイカ',
    277: 'ミツバウツギ',
    279: 'ベンゾイン',
    627: 'ターペスルート',
    733: 'コセンダングサ',
    743: 'ヒレアザミ',
    747: 'ヤグルマギク',
    749: 'セイヨウヤグルマギク',
    769: 'カラミント',
    771: 'ヤブイヌハッカ',
    773: 'モルダビアンバーム',
    779: 'ヒソップ',
    785: 'ホアハウンド',
    801: 'アミ',
    803: 'アメリカアンジェリカ',
    821: 'ドクゼリ',
    841: 'レッドジンジャー',
    845: 'ホワイトジンジャーリリー',
    857: 'キンミズヒキ',
    861: 'レディースマントル',
    881: 'トルメンチル',
    898: 'キマメ',
    901: 'カロブ',
    902: 'ヒヨコマメ',
    904: 'スナヘンプ',
    905: 'グアー',
    914: 'トリカブト',
    916: 'ニワトリカブト',
    923: 'オダマキ',
    925: 'リュウキンカ',
    926: 'ブラックコホシュ',
    931: 'セツブンソウ',
    932: 'ライム',
    936: 'ミカン',
    941: 'ミヤマシキミ',
    962: 'ハネタバコ',
    964: 'タバコ',
    968: 'カロライナホースネトル',
    971: 'ジャスミンナイトシェード',
    975: 'アシュワガンダ',
    976: 'クサノオウ',
    982: 'ダッチマンズブリーチーズ',
    983: 'ワイルドブリーディングハート',
    985: 'ケマンソウ',
}

conn = sqlite3.connect(DB_PATH)
conn.execute('PRAGMA encoding = "UTF-8"')
cur = conn.cursor()

updated = 0
for pid, ja_name in JA_FIXES2.items():
    cur.execute("SELECT length(paintingname_ja) FROM museum_item WHERE id=?", (pid,))
    row = cur.fetchone()
    if row and row[0] > 30:
        cur.execute("UPDATE museum_item SET paintingname_ja=? WHERE id=?", (ja_name, pid))
        updated += 1

conn.commit()
print(f"Updated: {updated}")

cur.execute("SELECT COUNT(*) FROM museum_item WHERE length(paintingname_ja) > 30")
print(f"Remaining long JA entries: {cur.fetchone()[0]}")
conn.close()
