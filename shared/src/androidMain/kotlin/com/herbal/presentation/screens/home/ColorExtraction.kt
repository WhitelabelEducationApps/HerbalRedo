package com.herbal.presentation.screens.home

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import com.whitelabel.platform.utils.ExtractedColors
import com.whitelabel.platform.utils.extractColorsFromDrawable

/**
 * Remember extracted colors from a drawable resource.
 * Uses Palette API to extract vibrant and muted colors.
 *
 * @param siteId The site ID for cache key
 * @param drawableResourceId The drawable resource ID to extract colors from
 * @return ExtractedColors or null if extraction fails
 */
@Composable
actual fun rememberExtractedColors(siteId: Long, drawableResourceId: Int?): ExtractedColors? {
    val context = LocalContext.current
    
    return if (drawableResourceId != null && drawableResourceId != 0) {
        remember(siteId, drawableResourceId) {
            // Synchronous extraction for Compose remember
            // In production, you might want to use LaunchedEffect for async extraction
            try {
                val drawable = context.getDrawable(drawableResourceId)
                val bitmap = drawable?.toBitmap(width = 100, height = 100)
                
                if (bitmap != null) {
                    val palette = androidx.palette.graphics.Palette.from(bitmap).generate()
                    
                    ExtractedColors(
                        vibrant = palette.vibrantSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        vibrantDark = palette.darkVibrantSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        vibrantLight = palette.lightVibrantSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        muted = palette.mutedSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        mutedDark = palette.darkMutedSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        mutedLight = palette.lightMutedSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) },
                        dominant = palette.dominantSwatch?.rgb?.let { androidx.compose.ui.graphics.Color(it) }
                    )
                } else {
                    null
                }
            } catch (e: Exception) {
                null
            }
        }
    } else {
        null
    }
}

/**
 * Extension function to convert Drawable to Bitmap
 */
private fun android.graphics.drawable.Drawable.toBitmap(width: Int, height: Int): android.graphics.Bitmap {
    val bitmap = android.graphics.Bitmap.createBitmap(width, height, android.graphics.Bitmap.Config.ARGB_8888)
    val canvas = android.graphics.Canvas(bitmap)
    setBounds(0, 0, width, height)
    draw(canvas)
    return bitmap
}
