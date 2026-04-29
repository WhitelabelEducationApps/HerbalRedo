package com.herbal.presentation.components

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import com.herbal.data.models.HeritageSite
import com.herbal.utils.getDrawableIdForSite
import com.herbal.utils.toDrawableResourceName

/**
 * Android implementation that uses getDrawableIdForSite to look up local drawable resources.
 */
@Composable
actual fun getSiteDrawableId(site: HeritageSite): Int? {
    val context = LocalContext.current
    return context.getDrawableIdForSite(site.name)
}

/**
 * Returns all drawable resource IDs for a site: primary + numbered variants (_2.._6).
 * Probing stops at the first missing index.
 */
@Composable
actual fun getSiteDrawableIds(site: HeritageSite): List<Int> {
    val context = LocalContext.current
    val baseName = site.name.toDrawableResourceName()
    val ids = mutableListOf<Int>()
    val primary = context.resources.getIdentifier(baseName, "drawable", context.packageName)
    if (primary != 0) ids.add(primary)
    for (i in 2..6) {
        val id = context.resources.getIdentifier("${baseName}_$i", "drawable", context.packageName)
        if (id != 0) ids.add(id) else break
    }
    return ids
}
