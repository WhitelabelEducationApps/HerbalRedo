package com.whitelabel.core.domain.language

enum class SupportedLanguage(val code: String, val displayName: String, val nativeName: String) {
    ENGLISH("en", "English", "English"),
    ROMANIAN("ro", "Romanian", "Română"),
    ITALIAN("it", "Italian", "Italiano"),
    SPANISH("es", "Spanish", "Español"),
    GERMAN("de", "German", "Deutsch"),
    FRENCH("fr", "French", "Français"),
    PORTUGUESE("pt", "Portuguese", "Português"),
    RUSSIAN("ru", "Russian", "Русский"),
    ARABIC("ar", "Arabic", "العربية"),
    CHINESE("zh", "Chinese", "中文"),
    JAPANESE("ja", "Japanese", "日本語"),
    TURKISH("tr", "Turkish", "Türkçe"),
    HINDI("hi", "Hindi", "हिन्दी"),
    HUNGARIAN("hu", "Hungarian", "Magyar"),
    POLISH("pl", "Polish", "Polski");

    companion object {
        fun fromCode(code: String?): SupportedLanguage =
            entries.find { it.code == code } ?: ENGLISH
    }
}
