package com.herbal.data.models

import com.herbal.utils.LanguagePreferences
import com.herbal.utils.SupportedLanguage
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.LocalizedFieldSet

data class HeritageSite(
    override val id: Long,
    override val name: String,
    val author: String?,
    override val description: String?,
    val location: String?,
    val style: String?,
    val imageUrl: String?,
    override val isFavorite: Boolean = false,
    override val wasViewed: Boolean = false,
    // Localized names
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
    val nameHu: String? = null,
    val nameHi: String? = null,
    val nameTr: String? = null,
    val namePl: String? = null,
    // Localized descriptions
    val descriptionRo: String? = null,
    val descriptionIt: String? = null,
    val descriptionEs: String? = null,
    val descriptionDe: String? = null,
    val descriptionFr: String? = null,
    val descriptionPt: String? = null,
    val descriptionRu: String? = null,
    val descriptionAr: String? = null,
    val descriptionZh: String? = null,
    val descriptionJa: String? = null,
    val descriptionNl: String? = null,
    val descriptionHu: String? = null,
    val descriptionHi: String? = null,
    val descriptionPl: String? = null,
    val descriptionTr: String? = null,
    // Localized styles
    val styleRo: String? = null,
    val styleIt: String? = null,
    val styleEs: String? = null,
    val styleDe: String? = null,
    val styleFr: String? = null,
    val stylePt: String? = null,
    val styleRu: String? = null,
    val styleAr: String? = null,
    val styleZh: String? = null,
    val styleJa: String? = null,
    val styleTr: String? = null,
    val styleHi: String? = null,
    val styleHu: String? = null,
    val stylePl: String? = null,
    // Colors and location
    override val primaryColor: Int? = null,
    override val secondaryColor: Int? = null,
    override val backgroundColor: Int? = null,
    override val detailColor: Int? = null,
    override val latitude: Double? = null,
    override val longitude: Double? = null,
    override val localizedFields: LocalizedFieldSet = LocalizedFieldSet()
) : DisplayableItem {

    override val imageUrls: List<String>
        get() = imageUrl?.split(",")?.map { it.trim() } ?: emptyList()

    override val category: String?
        get() = style

    override val groupKey: String?
        get() = author

    val countries: List<String>
        get() = author?.split(",")?.map { it.trim() } ?: emptyList()

    // Legacy no-arg methods using global state (backward compat for existing callers)
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
            SupportedLanguage.TURKISH -> nameTr
            SupportedLanguage.HINDI -> nameHi
            SupportedLanguage.HUNGARIAN -> nameHu
            SupportedLanguage.POLISH -> namePl
            SupportedLanguage.ENGLISH -> null
        } ?: name
    }

    fun getLocalizedDescription(): String? {
        val language = SupportedLanguage.fromCode(LanguagePreferences.getEffectiveLanguage())
        return when (language) {
            SupportedLanguage.ROMANIAN -> descriptionRo
            SupportedLanguage.ITALIAN -> descriptionIt
            SupportedLanguage.SPANISH -> descriptionEs
            SupportedLanguage.GERMAN -> descriptionDe
            SupportedLanguage.FRENCH -> descriptionFr
            SupportedLanguage.PORTUGUESE -> descriptionPt
            SupportedLanguage.RUSSIAN -> descriptionRu
            SupportedLanguage.ARABIC -> descriptionAr
            SupportedLanguage.CHINESE -> descriptionZh
            SupportedLanguage.JAPANESE -> descriptionJa
            SupportedLanguage.HINDI -> descriptionHi
            SupportedLanguage.HUNGARIAN -> descriptionHu
            SupportedLanguage.POLISH -> descriptionPl
            SupportedLanguage.TURKISH -> descriptionTr
            SupportedLanguage.ENGLISH -> description
        } ?: description
    }

    fun getLocalizedStyle(): String? {
        val language = SupportedLanguage.fromCode(LanguagePreferences.getEffectiveLanguage())
        return when (language) {
            SupportedLanguage.ROMANIAN -> styleRo
            SupportedLanguage.ITALIAN -> styleIt
            SupportedLanguage.SPANISH -> styleEs
            SupportedLanguage.GERMAN -> styleDe
            SupportedLanguage.FRENCH -> styleFr
            SupportedLanguage.PORTUGUESE -> stylePt
            SupportedLanguage.RUSSIAN -> styleRu
            SupportedLanguage.ARABIC -> styleAr
            SupportedLanguage.CHINESE -> styleZh
            SupportedLanguage.JAPANESE -> styleJa
            SupportedLanguage.POLISH -> stylePl
            SupportedLanguage.HINDI -> styleHi
            SupportedLanguage.HUNGARIAN -> styleHu
            SupportedLanguage.TURKISH -> styleTr
            SupportedLanguage.ENGLISH -> null
        } ?: style
    }
}
