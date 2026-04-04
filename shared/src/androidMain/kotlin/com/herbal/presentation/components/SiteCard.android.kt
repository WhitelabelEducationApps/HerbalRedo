package com.herbal.presentation.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import com.herbal.data.models.HeritageSite
import com.herbal.utils.getDrawableIdForSite

/**
 * Android implementation that uses getDrawableIdForSite to look up local drawable resources.
 */
@Composable
actual fun getSiteDrawableId(site: HeritageSite): Int? {
    val context = LocalContext.current
    return context.getDrawableIdForSite(site.name)
}
