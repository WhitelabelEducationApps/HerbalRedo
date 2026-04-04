package com.herbal.utils

// Re-export string utilities from whitelabel-platform

/**
 * Convert a name to a valid drawable resource name.
 * Delegates to platform's sanitizeForResourceName.
 */
fun String.toDrawableResourceName(): String {
    return com.whitelabel.platform.utils.sanitizeForResourceName(this)
}
