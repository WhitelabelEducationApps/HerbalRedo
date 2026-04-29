package com.herbal.utils

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.core.content.ContextCompat

@Composable
actual fun rememberLocationPermissionLauncher(
    onGranted: () -> Unit,
    onDenied: () -> Unit
): () -> Unit {
    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) onGranted() else onDenied()
    }
    return { launcher.launch(Manifest.permission.ACCESS_FINE_LOCATION) }
}

actual fun hasLocationPermission(context: Any): Boolean {
    if (context !is Context) return false
    return ContextCompat.checkSelfPermission(
        context, Manifest.permission.ACCESS_FINE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED
}
