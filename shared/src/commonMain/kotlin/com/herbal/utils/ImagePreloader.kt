package com.herbal.utils

import coil3.ImageLoader
import coil3.PlatformContext
import com.herbal.data.models.HeritageSite
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.debugLogI
import com.whitelabel.platform.utils.logImageLoad

private const val TAG = "ImagePreloader"

// Re-export from whitelabel-platform with museum-specific extensions and logging

class ImagePreloader(
    context: PlatformContext,
    imageLoader: ImageLoader
) {
    private val platformPreloader = com.whitelabel.platform.utils.ImagePreloader(
        context, 
        imageLoader, 
        "MuseumApp"
    )

    suspend fun preloadImages(
        sites: List<HeritageSite>,
        currentIndex: Int,
        preloadCount: Int = 15
    ) {
        val startIndex = currentIndex.coerceAtLeast(0)
        val endIndex = (currentIndex + preloadCount).coerceAtMost(sites.size - 1)
        val actualCount = endIndex - startIndex
        
        debugLogD(TAG, "Preloading $actualCount images from index $startIndex to $endIndex")
        
        // Use platform preloader with museum-specific extractors
        val itemsToPreload = sites.subList(startIndex, endIndex)
        var preloadedCount = 0
        var skippedCount = 0
        
        itemsToPreload.forEach { site ->
            val imageUrl = site.imageUrl?.split(",")?.firstOrNull()?.trim()
            if (!imageUrl.isNullOrBlank()) {
                val cacheKey = getThumbnailCacheKey(site.id)
                debugLogD(TAG, "Preloading image for site ${site.id}: $imageUrl")
                platformPreloader.preloadImage(
                    imageUrl = imageUrl,
                    cacheKey = cacheKey
                )
                preloadedCount++
            } else {
                debugLogD(TAG, "Skipping site ${site.id}, no image URL")
                skippedCount++
            }
        }
        
        debugLogI(TAG, "Preload complete: $preloadedCount images loaded, $skippedCount skipped")
    }

    fun clearCache() {
        debugLogD(TAG, "Clearing image cache")
        platformPreloader.clearCache()
    }
}

// Cache key functions that delegate to platform
fun getThumbnailCacheKey(siteId: Long): String {
    return com.whitelabel.platform.utils.getThumbnailCacheKey(siteId, "site")
}

fun getFullImageCacheKey(siteId: Long): String {
    return com.whitelabel.platform.utils.getFullImageCacheKey(siteId, "site")
}
