package com.whitelabel.core.presentation.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

@Composable
fun WhitelabelTheme(
    config: AppThemeConfig,
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) {
        darkColorScheme(
            primary = config.darkPrimary,
            onPrimary = config.darkOnPrimary,
            secondary = config.darkSecondary,
            background = config.darkBackground,
            surface = config.darkSurface
        )
    } else {
        lightColorScheme(
            primary = config.lightPrimary,
            onPrimary = config.lightOnPrimary,
            secondary = config.lightSecondary,
            background = config.lightBackground,
            surface = config.lightSurface
        )
    }
    MaterialTheme(colorScheme = colorScheme, content = content)
}
