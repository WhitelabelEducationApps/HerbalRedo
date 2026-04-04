package com.herbal.data.models

import com.herbal.utils.LanguagePreferences
import com.herbal.utils.SupportedLanguage
import com.whitelabel.core.domain.model.GroupMetadata
import com.whitelabel.core.domain.model.LocalizedFieldSet

data class Country(
    override val name: String,
    val nameRo: String? = null,
    val nameIt: String? = null,
    val nameEs: String? = null,
    val nameDe: String? = null,
    val nameFr: String? = null,
    val namePt: String? = null,
    val nameRu: String? = null,
    val nameAr: String? = null,
    val nameZh: String? = null,
    val nameJa: String? = null,
    val nameTr: String? = null,
    val namePl: String? = null,
    val nameHu: String? = null,
    val nameHi: String? = null
) : GroupMetadata {

    override val key: String get() = name

    override val localizedFields: LocalizedFieldSet
        get() = LocalizedFieldSet(
            names = buildMap {
                nameRo?.let { put("ro", it) }
                nameIt?.let { put("it", it) }
                nameEs?.let { put("es", it) }
                nameDe?.let { put("de", it) }
                nameFr?.let { put("fr", it) }
                namePt?.let { put("pt", it) }
                nameRu?.let { put("ru", it) }
                nameAr?.let { put("ar", it) }
                nameZh?.let { put("zh", it) }
                nameJa?.let { put("ja", it) }
                nameTr?.let { put("tr", it) }
                namePl?.let { put("pl", it) }
                nameHu?.let { put("hu", it) }
                nameHi?.let { put("hi", it) }
            }
        )

    // Legacy no-arg method (backward compat)
    fun getLocalizedName(): String {
        val language = SupportedLanguage.fromCode(LanguagePreferences.getEffectiveLanguage())
        return when (language) {
            SupportedLanguage.ROMANIAN -> nameRo
            SupportedLanguage.ITALIAN -> nameIt
            SupportedLanguage.SPANISH -> nameEs
            SupportedLanguage.GERMAN -> nameDe
            SupportedLanguage.FRENCH -> nameFr
            SupportedLanguage.PORTUGUESE -> namePt
            SupportedLanguage.RUSSIAN -> nameRu
            SupportedLanguage.ARABIC -> nameAr
            SupportedLanguage.CHINESE -> nameZh
            SupportedLanguage.JAPANESE -> nameJa
            SupportedLanguage.ENGLISH -> name
            SupportedLanguage.HINDI -> nameHi
            SupportedLanguage.HUNGARIAN -> nameHu
            SupportedLanguage.TURKISH -> nameTr
            SupportedLanguage.POLISH -> namePl
        } ?: name
    }
}
