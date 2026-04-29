package com.herbal.utils

import androidx.compose.runtime.Composable

/**
 * Returns a lambda that, when invoked, launches a location permission request.
 * [onGranted] is called if the user grants ACCESS_FINE_LOCATION.
 * [onDenied] is called if the user denies it.
 */
@Composable
expect fun rememberLocationPermissionLauncher(
    onGranted: () -> Unit,
    onDenied: () -> Unit
): () -> Unit

/**
 * Returns true if ACCESS_FINE_LOCATION is already granted.
 * [context] is the platform context (android.content.Context on Android).
 */
expect fun hasLocationPermission(context: Any): Boolean
