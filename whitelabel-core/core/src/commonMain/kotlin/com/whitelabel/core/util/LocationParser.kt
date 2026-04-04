package com.whitelabel.core.util

/**
 * Parses location strings in format "longitude,latitude"
 * where comma is used as decimal separator within each number.
 * Example: "67,82525,34,84694" → Pair(67.82525, 34.84694)
 */
object LocationParser {
    fun parse(location: String?): Pair<Double, Double>? {
        if (location.isNullOrBlank()) return null

        return try {
            val parts = location.split(",")
            if (parts.size == 4) {
                val longitude = "${parts[0]}.${parts[1]}".toDouble()
                val latitude = "${parts[2]}.${parts[3]}".toDouble()
                Pair(longitude, latitude)
            } else if (parts.size == 2) {
                val longitude = parts[0].toDouble()
                val latitude = parts[1].toDouble()
                Pair(longitude, latitude)
            } else {
                null
            }
        } catch (e: NumberFormatException) {
            null
        }
    }
}
