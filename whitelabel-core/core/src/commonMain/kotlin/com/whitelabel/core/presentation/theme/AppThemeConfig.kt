package com.whitelabel.core.presentation.theme

import androidx.compose.ui.graphics.Color

/**
 * App-provided theme configuration. Each whitelabel app supplies its own colors.
 */
data class AppThemeConfig(
    val lightPrimary: Color,
    val lightOnPrimary: Color,
    val lightSecondary: Color,
    val lightBackground: Color,
    val lightSurface: Color,
    val darkPrimary: Color,
    val darkOnPrimary: Color,
    val darkSecondary: Color,
    val darkBackground: Color,
    val darkSurface: Color
)
