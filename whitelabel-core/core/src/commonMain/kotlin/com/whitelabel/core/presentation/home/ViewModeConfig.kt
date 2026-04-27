package com.whitelabel.core.presentation.home

import com.whitelabel.core.AppConfig

/**
 * Provides available view modes based on app configuration.
 * Map view is only available if enabled in AppConfig.
 */
fun AppConfig.getAvailableViewModes(): List<ViewMode> {
    return listOfNotNull(
        ViewMode.Grid,
        if (enableMap) ViewMode.Map else null
    )
}

/**
 * Check if view mode switcher should be displayed.
 * Only show if multiple view modes are available.
 */
fun AppConfig.shouldShowViewModeSwitcher(): Boolean {
    return getAvailableViewModes().size > 1
}

/**
 * Get default view mode based on availability.
 * Prefers Grid, falls back to Map if Grid is unavailable (unlikely).
 */
fun AppConfig.getDefaultViewMode(): ViewMode {
    return getAvailableViewModes().firstOrNull() ?: ViewMode.Grid
}
