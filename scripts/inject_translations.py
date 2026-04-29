#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "androidApp/src/main/res"

FOLDER_MAP = {
    "ar": "values-ar", "de": "values-de", "es": "values-es",
    "fr": "values-fr", "hi": "values-hi", "hu": "values-hu",
    "it": "values-it", "ja": "values-ja", "pl": "values-pl",
    "pt": "values-pt", "ro": "values-ro", "ru": "values-ru",
    "tr": "values-tr", "zh": "values-zh-rCN",
}

TRANSLATIONS = {
    "ar": {
        "use_location_plants": "النباتات المحلية فقط",
        "onboarding_title": "اكتشف النباتات المحلية",
        "onboarding_message": "افتح القائمة الجانبية وفعّل \\'النباتات المحلية فقط\\' لرؤية النباتات التي تنمو بشكل طبيعي في منطقتك.",
        "onboarding_ok": "فهمت",
        "location_permission_denied": "تم رفض إذن الموقع. تم تعطيل التصفية.",
    },
    "de": {
        "use_location_plants": "Nur lokale Pflanzen",
        "onboarding_title": "Entdecke lokale Pflanzen",
        "onboarding_message": "Öffne das Seitenmenü und aktiviere \\'Nur lokale Pflanzen\\', um Pflanzen zu sehen, die nativ in deiner Region wachsen.",
        "onboarding_ok": "Verstanden",
        "location_permission_denied": "Standortzugriff verweigert. Filter deaktiviert.",
    },
    "es": {
        "use_location_plants": "Solo plantas locales",
        "onboarding_title": "Descubre plantas locales",
        "onboarding_message": "Abre el menú lateral y activa \\'Solo plantas locales\\' para ver plantas que crecen de forma nativa en tu región.",
        "onboarding_ok": "Entendido",
        "location_permission_denied": "Permiso de ubicación denegado. Filtro desactivado.",
    },
    "fr": {
        "use_location_plants": "Plantes locales seulement",
        "onboarding_title": "Découvrez les plantes locales",
        "onboarding_message": "Ouvrez le menu latéral et activez \\'Plantes locales seulement\\' pour voir les plantes qui poussent naturellement dans votre région.",
        "onboarding_ok": "Compris",
        "location_permission_denied": "Accès à la localisation refusé. Filtre désactivé.",
    },
    "hi": {
        "use_location_plants": "केवल स्थानीय पौधे",
        "onboarding_title": "स्थानीय पौधों की खोज करें",
        "onboarding_message": "साइड मेनू खोलें और \\'केवल स्थानीय पौधे\\' को सक्षम करें ताकि आप अपने क्षेत्र में प्राकृतिक रूप से उगने वाले पौधों को देख सकें।",
        "onboarding_ok": "समझ गए",
        "location_permission_denied": "स्थान अनुमति अस्वीकृत। फ़िल्टर अक्षम।",
    },
    "hu": {
        "use_location_plants": "Csak helyi növények",
        "onboarding_title": "Fedezd fel a helyi növényeket",
        "onboarding_message": "Nyisd meg az oldalsó menüt, és engedélyezd a \\'Csak helyi növények\\' opciót, hogy lásd a területeden természetesen növő növényeket.",
        "onboarding_ok": "Értem",
        "location_permission_denied": "Helymeghatározás megtagadva. Szűrő letiltva.",
    },
    "it": {
        "use_location_plants": "Solo piante locali",
        "onboarding_title": "Scopri piante locali",
        "onboarding_message": "Apri il menu laterale e attiva \\'Solo piante locali\\' per vedere le piante che crescono naturalmente nella tua regione.",
        "onboarding_ok": "Capito",
        "location_permission_denied": "Permesso posizione negato. Filtro disattivato.",
    },
    "ja": {
        "use_location_plants": "地元の植物のみ",
        "onboarding_title": "地元の植物を発見",
        "onboarding_message": "サイドメニューを開き「地元の植物のみ」を有効にして、あなたの地域に自生する植物を表示してください。",
        "onboarding_ok": "了解",
        "location_permission_denied": "位置情報の許可が拒否されました。フィルター無効。",
    },
    "pl": {
        "use_location_plants": "Tylko lokalne rośliny",
        "onboarding_title": "Odkryj lokalne rośliny",
        "onboarding_message": "Otwórz menu boczne i włącz \\'Tylko lokalne rośliny\\', aby zobaczyć rośliny rosnące naturalnie w Twoim regionie.",
        "onboarding_ok": "Rozumiem",
        "location_permission_denied": "Odmowa dostępu do lokalizacji. Filtr wyłączony.",
    },
    "pt": {
        "use_location_plants": "Apenas plantas locais",
        "onboarding_title": "Descubra plantas locais",
        "onboarding_message": "Abra o menu lateral e ative \\'Apenas plantas locais\\' para ver plantas que crescem nativamente na sua região.",
        "onboarding_ok": "Entendi",
        "location_permission_denied": "Permissão de localização negada. Filtro desativado.",
    },
    "ro": {
        "use_location_plants": "Doar plante locale",
        "onboarding_title": "Descoperă plante locale",
        "onboarding_message": "Deschide meniul lateral și activează \\'Doar plante locale\\' pentru a vedea plantele care cresc natural în regiunea ta.",
        "onboarding_ok": "Înțeles",
        "location_permission_denied": "Permisiune locație refuzată. Filtrul este dezactivat.",
    },
    "ru": {
        "use_location_plants": "Только местные растения",
        "onboarding_title": "Найдите местные растения",
        "onboarding_message": "Откройте боковое меню и включите \\'Только местные растения\\', чтобы увидеть растения, растущие в вашем регионе.",
        "onboarding_ok": "Понятно",
        "location_permission_denied": "Доступ к геолокации запрещён. Фильтр отключён.",
    },
    "tr": {
        "use_location_plants": "Yalnızca Yerel Bitkiler",
        "onboarding_title": "Yerel Bitkileri Keşfedin",
        "onboarding_message": "Yan menüyü açın ve \\'Yalnızca Yerel Bitkiler\\' seçeneğini etkinleştirin; bölgenizde doğal olarak yetişen bitkileri görün.",
        "onboarding_ok": "Anladım",
        "location_permission_denied": "Konum izni reddedildi. Filtre devre dışı.",
    },
    "zh": {
        "use_location_plants": "仅本地植物",
        "onboarding_title": "发现本地植物",
        "onboarding_message": "打开侧边菜单并启用\\'仅本地植物\\'，以查看在您所在地区自然生长的植物。",
        "onboarding_ok": "明白了",
        "location_permission_denied": "位置权限被拒绝。过滤器已禁用。",
    },
}

KEYS = ["use_location_plants", "onboarding_title", "onboarding_message", "onboarding_ok", "location_permission_denied"]

for lang, folder in FOLDER_MAP.items():
    path = BASE / folder / "strings.xml"
    content = path.read_text(encoding="utf-8")
    t = TRANSLATIONS[lang]
    insert = ""
    for key in KEYS:
        if f'name="{key}"' not in content:
            insert += f'\n    <string name="{key}">{t[key]}</string>'
    if insert:
        content = content.replace("</resources>", insert + "\n</resources>")
        path.write_text(content, encoding="utf-8")
        print(f"  OK    {folder}")
    else:
        print(f"  SKIP  {folder} (already has all strings)")

print("\nDone.")
