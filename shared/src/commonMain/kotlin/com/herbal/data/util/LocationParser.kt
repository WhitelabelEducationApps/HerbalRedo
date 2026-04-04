package com.herbal.data.util

object LocationParser {

    fun parse(location: String?): Pair<Double, Double>? {
        if (location.isNullOrBlank()) {
            return null
        }

        val parts = location.split(',').map { it.trim() }
        var lat: Double? = null
        var long: Double? = null

        when (parts.size) {
            // Case: "lat, long" - 2 parts
            2 -> {
                lat = parts[0].toDoubleOrNull()
                long = parts[1].toDoubleOrNull()
            }
            3 -> {
                if (parts[0].length == 2 && parts[1].length != 2) {
                    lat = (parts[0] + "." + parts[1]).toDoubleOrNull()
                    long = parts[2].toDoubleOrNull()
                } else {
                    lat = parts[0].toDoubleOrNull()
                    long = (parts[1] + "." + parts[2]).toDoubleOrNull()
                }
            }
            4 -> {
                lat = (parts[0] + "." + parts[1]).toDoubleOrNull()
                long = (parts[2] + "." + parts[3]).toDoubleOrNull()
            }
        }
        return Pair(lat ?: 0.0, long ?: 0.0)
    }
}
