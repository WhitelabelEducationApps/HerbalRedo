package com.herbal.utils

import androidx.compose.ui.graphics.Color
import com.herbal.data.models.HeritageSite
import com.whitelabel.platform.utils.toComposeColor as platformToComposeColor
import com.whitelabel.platform.utils.blendColors as platformBlendColors
import com.whitelabel.platform.utils.calculateCardBackgroundColor

/**
 * Convert an ARGB integer to a Compose Color.
 * Extension function that delegates to platform utility.
 */
fun Int?.toComposeColor(default: Color = Color.Gray): Color {
    return platformToComposeColor(this, default)
}

/**
 * Blend two colors together with a given ratio.
 */
fun blendColors(color1: Color, color2: Color, ratio: Float): Color {
    return platformBlendColors(color1, color2, ratio)
}

/**
 * Get the card background color for a HeritageSite.
 * Uses the platform's calculateCardBackgroundColor with museum defaults.
 */
fun HeritageSite.getCardBackgroundColor(): Color {
    return com.whitelabel.platform.utils.calculateCardBackgroundColor(
        primaryColor = primaryColor,
        secondaryColor = secondaryColor,
        backgroundColor = backgroundColor,
        defaultPrimary = Color(0xFFE0E0E0),
        defaultSecondary = Color(0xFFBDBDBD),
        defaultBackground = Color(0xFFF5F5F5),
        primarySecondaryRatio = 0.75f,
        finalBlendRatio = 0.2f
    )
}

/**
 * Get the primary color for a HeritageSite.
 */
fun HeritageSite.getPrimaryColor(default: Color = Color(0xFF6200EE)): Color {
    return primaryColor.toComposeColor(default)
}

/**
 * Get the secondary color for a HeritageSite.
 */
fun HeritageSite.getSecondaryColor(default: Color = Color(0xFF03DAC6)): Color {
    return secondaryColor.toComposeColor(default)
}

/**
 * Get the background color for a HeritageSite.
 */
fun HeritageSite.getBackgroundColor(default: Color = Color(0xFFF5F5F5)): Color {
    return backgroundColor.toComposeColor(default)
}

/**
 * Get the detail color for a HeritageSite.
 */
fun HeritageSite.getDetailColor(default: Color = Color(0xFF6200EE)): Color {
    return detailColor.toComposeColor(default)
}
