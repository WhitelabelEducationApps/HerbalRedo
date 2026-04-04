package com.herbal.presentation.screens.site

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import coil3.request.ImageRequest

@Composable
actual fun imageRequestBuilder(): ImageRequest.Builder {
    return ImageRequest.Builder(LocalContext.current)
}