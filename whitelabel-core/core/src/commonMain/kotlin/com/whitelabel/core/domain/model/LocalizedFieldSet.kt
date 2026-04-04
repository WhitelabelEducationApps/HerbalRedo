package com.whitelabel.core.domain.model

/**
 * Language-agnostic container for localized text fields.
 * Replaces per-language nullable properties (nameRo, nameIt, etc.)
 * with simple map lookups.
 */
data class LocalizedFieldSet(
    private val names: Map<String, String> = emptyMap(),
    private val descriptions: Map<String, String> = emptyMap(),
    private val categories: Map<String, String> = emptyMap()
) {
    fun getName(languageCode: String): String? = names[languageCode]
    fun getDescription(languageCode: String): String? = descriptions[languageCode]
    fun getCategory(languageCode: String): String? = categories[languageCode]
}
