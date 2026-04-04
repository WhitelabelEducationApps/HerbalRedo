package com.whitelabel.core.domain.model

/**
 * Core abstraction for any displayable catalog item.
 * Apps implement this with their concrete models (HeritageSite, Painting, etc.)
 */
interface DisplayableItem {
    val id: Long
    val name: String
    val description: String?
    val imageUrls: List<String>
    val category: String?
    val groupKey: String?
    val isFavorite: Boolean
    val wasViewed: Boolean
    val latitude: Double?
    val longitude: Double?
    val primaryColor: Int?
    val secondaryColor: Int?
    val backgroundColor: Int?
    val detailColor: Int?
    val localizedFields: LocalizedFieldSet

    fun getLocalizedName(languageCode: String): String =
        localizedFields.getName(languageCode) ?: name

    fun getLocalizedDescription(languageCode: String): String? =
        localizedFields.getDescription(languageCode) ?: description

    fun getLocalizedCategory(languageCode: String): String? =
        localizedFields.getCategory(languageCode) ?: category
}
