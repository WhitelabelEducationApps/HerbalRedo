package com.herbal.presentation.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.herbal.data.models.HeritageSite
import com.whitelabel.platform.presentation.components.MapView as PlatformMapView
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logUserAction

private const val TAG = "MapView"

/**
 * Re-export MapView from whitelabel-platform for HeritageSite with logging.
 */
@Composable
fun MapView(
    sites: List<HeritageSite>,
    focusedSiteId: Long? = null,
    onSiteClick: (Long) -> Unit,
    onClearFocusedSite: () -> Unit = {},
    modifier: Modifier = Modifier
) {
    debugLogD(TAG, "Rendering MapView with ${sites.size} sites, focused=$focusedSiteId")
    
    PlatformMapView(
        items = sites,
        focusedItemId = focusedSiteId,
        onItemClick = { siteId ->
            logUserAction(TAG, "clicked map marker", "siteId=$siteId")
            onSiteClick(siteId)
        },
        onClearFocusedItem = {
            debugLogD(TAG, "Clearing focused site")
            onClearFocusedSite()
        },
        modifier = modifier
    )
}
