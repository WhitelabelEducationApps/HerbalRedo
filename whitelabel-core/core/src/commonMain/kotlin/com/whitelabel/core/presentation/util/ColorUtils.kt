package com.whitelabel.core.presentation.util

import androidx.compose.ui.graphics.Color

fun Int?.toComposeColor(default: Color = Color.Gray): Color =
    if (this != null) Color(this) else default

fun blendColors(color1: Color, color2: Color, ratio: Float): Color {
    val r = ratio.coerceIn(0f, 1f)
    return Color(
        red = color1.red * (1 - r) + color2.red * r,
        green = color1.green * (1 - r) + color2.green * r,
        blue = color1.blue * (1 - r) + color2.blue * r,
        alpha = color1.alpha * (1 - r) + color2.alpha * r
    )
}
