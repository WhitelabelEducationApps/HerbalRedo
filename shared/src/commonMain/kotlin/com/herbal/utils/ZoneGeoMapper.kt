package com.herbal.utils

/**
 * Maps GPS coordinates to TDWG geographic zone IDs.
 * Uses offline bounding boxes — no internet required.
 *
 * Bounding boxes are intentionally generous (zones overlap) to handle edge cases.
 * Source: TDWG/WGSRPD World Geographical Scheme for Recording Plant Distributions.
 */
object ZoneGeoMapper {

    private data class BBox(val minLat: Double, val maxLat: Double, val minLng: Double, val maxLng: Double) {
        fun contains(lat: Double, lng: Double): Boolean =
            lat in minLat..maxLat && lng in minLng..maxLng
    }

    // Each zone is a list of bounding boxes (some zones have non-contiguous areas)
    private val zoneBBoxes: Map<String, List<BBox>> = mapOf(
        "zone_northern_europe" to listOf(
            BBox(54.0, 71.5, -25.0, 32.0)   // Scandinavia, UK, Iceland, Baltic states
        ),
        "zone_central_europe" to listOf(
            BBox(42.0, 58.0, 5.0, 25.0)      // Germany, France, Austria, Poland, Benelux, Switzerland
        ),
        "zone_southern_europe" to listOf(
            BBox(35.0, 48.0, -10.0, 37.0)    // Spain, Italy, Greece, Balkans, Turkey (European part)
        ),
        "zone_eastern_europe" to listOf(
            BBox(44.0, 60.0, 22.0, 42.0)     // Romania, Ukraine, Belarus, Moldova, W Russia
        ),
        "zone_northern_africa" to listOf(
            BBox(18.0, 38.0, -18.0, 37.0)    // Morocco, Algeria, Tunisia, Libya, Egypt
        ),
        "zone_western_africa" to listOf(
            BBox(-5.0, 20.0, -18.0, 16.0)    // West Africa (Senegal to Nigeria)
        ),
        "zone_eastern_africa" to listOf(
            BBox(-12.0, 22.0, 28.0, 51.0)    // Kenya, Tanzania, Ethiopia, Somalia, Uganda
        ),
        "zone_southern_africa" to listOf(
            BBox(-35.0, -8.0, 11.0, 40.0)    // South Africa, Zimbabwe, Mozambique, Namibia
        ),
        "zone_western_asia" to listOf(
            BBox(12.0, 42.0, 26.0, 63.0)     // Turkey (Asian), Levant, Iraq, Iran, Arabia, Caucasus
        ),
        "zone_central_asia" to listOf(
            BBox(36.0, 56.0, 51.0, 80.0)     // Kazakhstan, Uzbekistan, Turkmenistan, Afghanistan, Kyrgyzstan
        ),
        "zone_south_asia" to listOf(
            BBox(5.0, 37.0, 60.0, 97.0)      // India, Pakistan, Bangladesh, Sri Lanka, Nepal
        ),
        "zone_southeast_asia" to listOf(
            BBox(-10.0, 28.0, 92.0, 141.0)   // Thailand, Vietnam, Indonesia, Philippines, Myanmar
        ),
        "zone_east_asia" to listOf(
            BBox(20.0, 53.0, 100.0, 145.0)   // China, Japan, Korea, Taiwan
        ),
        "zone_siberia" to listOf(
            BBox(50.0, 75.0, 60.0, 170.0)    // Siberia & Russian Far East
        ),
        "zone_north_america_east" to listOf(
            BBox(25.0, 55.0, -97.0, -52.0)   // Eastern USA, Eastern Canada, Florida to Maritimes
        ),
        "zone_north_america_west" to listOf(
            BBox(25.0, 72.0, -170.0, -97.0)  // Western USA, Western Canada, Alaska, Pacific coast
        ),
        "zone_central_america" to listOf(
            BBox(7.0, 33.0, -120.0, -59.0)   // Mexico, Central America, Caribbean
        ),
        "zone_south_america_north" to listOf(
            BBox(-5.0, 13.0, -82.0, -34.0)   // Venezuela, Colombia, Brazil (north), Guyana, Ecuador
        ),
        "zone_south_america_south" to listOf(
            BBox(-56.0, -5.0, -82.0, -34.0)  // Peru, Bolivia, Brazil (south), Argentina, Chile
        ),
        "zone_australia_oceania" to listOf(
            BBox(-47.0, 0.0, 113.0, 180.0),  // Australia, New Zealand, Papua New Guinea
            BBox(-47.0, 30.0, -180.0, -120.0) // Pacific Islands (Polynesia, Melanesia)
        ),
        "zone_arctic" to listOf(
            BBox(66.5, 90.0, -180.0, 180.0)  // Arctic Circle and above
        ),
        "zone_tropical_africa" to listOf(
            BBox(-5.0, 15.0, 9.0, 45.0)      // Central/Equatorial Africa (Congo, Cameroon, Nigeria east)
        ),
    )

    /**
     * Returns the best-matching zone ID for the given GPS coordinates.
     * Returns null if no zone matches (very rare edge case — open ocean, etc.)
     */
    fun getZoneForLocation(lat: Double, lng: Double): String? {
        val matches = zoneBBoxes.entries.filter { (_, boxes) ->
            boxes.any { it.contains(lat, lng) }
        }.map { it.key }

        if (matches.isEmpty()) return null

        // If multiple boxes match (overlapping borders), prefer the most specific
        // Priority: smaller regions over larger catch-alls
        val priority = listOf(
            "zone_northern_europe", "zone_central_europe", "zone_southern_europe",
            "zone_eastern_europe", "zone_northern_africa", "zone_western_africa",
            "zone_eastern_africa", "zone_southern_africa", "zone_western_asia",
            "zone_central_asia", "zone_south_asia", "zone_southeast_asia",
            "zone_east_asia", "zone_siberia", "zone_north_america_east",
            "zone_north_america_west", "zone_central_america",
            "zone_south_america_north", "zone_south_america_south",
            "zone_australia_oceania", "zone_arctic", "zone_tropical_africa"
        )

        return matches.minByOrNull { priority.indexOf(it) }
    }
}
