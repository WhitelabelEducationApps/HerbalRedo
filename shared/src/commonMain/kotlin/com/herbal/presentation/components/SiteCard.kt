package com.herbal.presentation.components

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.herbal.data.models.HeritageSite
import com.herbal.utils.LanguagePreferences
import com.herbal.utils.getCardBackgroundColor
import com.whitelabel.platform.presentation.components.GenericSiteCard
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.debugLogI
import com.whitelabel.platform.utils.logUserAction

private const val TAG = "SiteCard"

/**
 * Get the drawable resource ID for a site.
 * Platform-specific implementation (Android uses getDrawableIdForSite).
 */
@Composable
expect fun getSiteDrawableId(site: HeritageSite): Int?

/**
 * Get all drawable resource IDs for a site (primary + numbered variants _2.._6).
 * Returns an empty list if no image is found at all.
 */
@Composable
expect fun getSiteDrawableIds(site: HeritageSite): List<Int>

/**
 * Herbal-specific SiteCard that displays plant names in the current locale.
 * Wraps GenericSiteCard from whitelabel-platform which uses localizedFields
 * from the DisplayableItem interface for name/description localization.
 */
@Composable
fun SiteCard(
    site: HeritageSite,
    onClick: () -> Unit,
    onFavoriteClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val drawableIds = getSiteDrawableIds(site)
    val drawableId = drawableIds.firstOrNull() ?: getSiteDrawableId(site)
    val imageUrl = site.imageUrl?.split(",")?.firstOrNull()?.trim()
    val selectedLanguage by LanguagePreferences.selectedLanguage.collectAsState()
    val languageCode = selectedLanguage?.code ?: "en"

    debugLogD(TAG, "Rendering SiteCard for site ${site.id}: ${site.name}, lang=$languageCode, drawableId=$drawableId")
    GenericSiteCard(
        item = site,
        languageCode = languageCode,
        onClick = {
            logUserAction(TAG, "clicked site card", "siteId=${site.id}, name=${site.name}")
            onClick()
        },
        onFavoriteClick = {
            logUserAction(TAG, "clicked favorite", "siteId=${site.id}, currentFavorite=${site.isFavorite}")
            onFavoriteClick()
        },
        modifier = modifier,
        imageUrl = imageUrl,
        drawableResourceId = drawableId,
        drawableResourceIds = drawableIds,
        imageHeight = 120.dp,
        cardColors = androidx.compose.material3.CardDefaults.cardColors(
            containerColor = site.getCardBackgroundColor()
        ),
        showFavorite = true,
        titleColor = Color.White
    )
}
