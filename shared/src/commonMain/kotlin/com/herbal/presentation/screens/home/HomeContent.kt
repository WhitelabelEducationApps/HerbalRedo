package com.herbal.presentation.screens.home

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.herbal.data.models.HeritageSite
import com.herbal.presentation.components.getSiteDrawableId
import com.herbal.utils.LanguagePreferences
import com.whitelabel.core.presentation.home.HomeUiState
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.platform.presentation.screens.home.HomeContent as PlatformHomeContent
import com.whitelabel.platform.utils.ExtractedColors
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logLifecycle

private const val TAG = "HomeContent"

/**
 * Museum-specific HomeContent that delegates to whitelabel-platform version
 * with museum-specific components.
 */
@Composable
fun HomeContent(
    uiState: HomeUiState,
    viewMode: ViewMode,
    searchQuery: String,
    focusedSiteId: Long? = null,
    onSiteClick: (Long) -> Unit,
    onFavoriteClick: (HeritageSite) -> Unit,
    onClearFocusedSite: () -> Unit = {},
    modifier: Modifier = Modifier,
    showCategory: Boolean = true
) {
    logLifecycle(TAG, "Composable entered, viewMode=$viewMode")

    val selectedLanguage by LanguagePreferences.selectedLanguage.collectAsState()
    val languageCode = selectedLanguage?.code ?: "en"

    DisposableEffect(uiState) {
        when (uiState) {
            is HomeUiState.Loading -> debugLogD(TAG, "State: Loading")
            is HomeUiState.Empty -> debugLogD(TAG, "State: Empty (query='$searchQuery')")
            is HomeUiState.Error -> debugLogD(TAG, "State: Error - ${uiState.message}")
            is HomeUiState.Success<*> -> {
                @Suppress("UNCHECKED_CAST")
                val success = uiState as HomeUiState.Success<HeritageSite>
                debugLogD(TAG, "State: Success - ${success.items.size} items, ${success.groups.size} groups")
            }
        }
        onDispose { }
    }

    PlatformHomeContent(
        uiState = uiState,
        viewMode = viewMode,
        languageCode = languageCode,
        searchQuery = searchQuery,
        focusedItemId = focusedSiteId,
        onItemClick = onSiteClick,
        onFavoriteClick = onFavoriteClick,
        onClearFocusedItem = onClearFocusedSite,
        modifier = modifier,
        gridColumns = 2,
        drawableResourceIdProvider = { site -> getSiteDrawableId(site) },
        colorExtractor = { site ->
            val drawableId = getSiteDrawableId(site)
            drawableId?.let { id ->
                rememberExtractedColors(site.id, id)
            }
        },
        showCategory = showCategory,
        listHeader = {
            if (uiState is HomeUiState.Success<*>) {
                @Suppress("UNCHECKED_CAST")
                val successState = uiState as HomeUiState.Success<HeritageSite>
                val context = LocalContext.current
                val plantCountText = try {
                    val pluralsId = context.resources.getIdentifier("plant_count", "plurals", context.packageName)
                    context.resources.getQuantityString(pluralsId, successState.items.size, successState.items.size)
                } catch (e: Exception) {
                    getPluralizedPlantCount(successState.items.size)
                }
                Text(
                    text = plantCountText,
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }
        },
        groupHeader = { group ->
            Column(modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = "${group.displayName} (${group.items.size})",
                    style = MaterialTheme.typography.headlineSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(top = 16.dp, bottom = 8.dp)
                )
                HorizontalDivider(
                    modifier = Modifier.fillMaxWidth(),
                    thickness = 1.dp,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    )
}

// Helper function to get pluralized plant count
private fun getPluralizedPlantCount(count: Int): String {
    return if (count == 1) {
        "$count Plant"
    } else {
        "$count Plants"
    }
}
