package com.herbal.utils

import android.annotation.SuppressLint
import android.content.Context
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

@SuppressLint("MissingPermission")
actual suspend fun getLocationLastKnown(context: Any): Pair<Double, Double>? {
    if (context !is Context) return null
    return suspendCancellableCoroutine { cont ->
        val client = LocationServices.getFusedLocationProviderClient(context)
        client.lastLocation
            .addOnSuccessListener { location ->
                if (location != null) {
                    cont.resume(Pair(location.latitude, location.longitude))
                } else {
                    cont.resume(null)
                }
            }
            .addOnFailureListener {
                cont.resume(null)
            }
    }
}
