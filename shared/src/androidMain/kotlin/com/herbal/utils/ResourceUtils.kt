package com.herbal.utils

import android.content.Context

/**
 * Get the drawable resource ID for a heritage site by name.
 * Returns null if the drawable doesn't exist.
 */
fun Context.getDrawableIdForSite(siteName: String): Int? {
    val resourceName = siteName.toDrawableResourceName()
    val resourceId = resources.getIdentifier(resourceName, "drawable", packageName)
    return if (resourceId != 0) resourceId else null
}
