package com.herbal.presentation.components

// Re-export from core so existing imports keep working
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier

@Composable
fun LoadingIndicator(modifier: Modifier = Modifier) =
    com.whitelabel.core.presentation.components.LoadingIndicator(modifier)
