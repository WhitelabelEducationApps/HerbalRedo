package com.herbal.utils

/**
 * Returns the last known GPS location as (latitude, longitude), or null if unavailable.
 * [context] is the platform context (android.content.Context on Android).
 * Requires location permission to already be granted before calling.
 */
expect suspend fun getLocationLastKnown(context: Any): Pair<Double, Double>?
