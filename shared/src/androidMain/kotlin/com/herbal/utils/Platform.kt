package com.herbal.utils

import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext
import coil3.PlatformContext

@Composable
actual fun getPlatformContext(): PlatformContext = LocalContext.current

@Composable
actual fun getDrawableResourceId(name: String): Int {
    val context = LocalContext.current
    return context.resources.getIdentifier(name, "drawable", context.packageName)
}

@Composable
actual fun getStringResource(id: String): String {
    val context = LocalContext.current
    val resourceId = context.resources.getIdentifier(id, "string", context.packageName)
    return context.getString(resourceId)
}
