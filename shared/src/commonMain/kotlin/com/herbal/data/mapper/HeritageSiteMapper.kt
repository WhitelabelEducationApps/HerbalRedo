package com.herbal.data.mapper

import com.herbal.data.local.Museum_item
import com.herbal.data.models.HeritageSite
import com.herbal.data.util.LocationParser
import com.whitelabel.core.domain.model.LocalizedFieldSet

object HeritageSiteMapper {

    fun Museum_item.toHeritageSite(): HeritageSite {
        val locationPair = LocationParser.parse(location)
        return HeritageSite(
            id = id ?: 0L,
            name = paintingname ?: "",
            author = author,
            description = description,
            location = location,
            style = style,
            imageUrl = full_image_uri,
            isFavorite = isFavourite == "true",
            wasViewed = viewed == "true",
            // Localized names (11 languages: ro, es, de, fr, it, ru, pt, zh, ja, ar, hi)
            nameRo = paintingname_ro,
            nameIt = paintingname_it,
            nameEs = paintingname_es,
            nameDe = paintingname_de,
            nameFr = paintingname_fr,
            namePt = paintingname_pt,
            nameRu = paintingname_ru,
            nameZh = paintingname_zh,
            nameJa = paintingname_ja,
            nameAr = paintingname_ar,
            nameHi = paintingname_hi,
            // Localized descriptions
            descriptionRo = description_ro,
            descriptionIt = description_it,
            descriptionEs = description_es,
            descriptionDe = description_de,
            descriptionFr = description_fr,
            descriptionPt = description_pt,
            descriptionRu = description_ru,
            descriptionZh = description_zh,
            descriptionJa = description_ja,
            descriptionAr = description_ar,
            descriptionHi = description_hi,
            // Localized styles
            styleRo = style_ro,
            styleIt = style_it,
            styleEs = style_es,
            styleDe = style_de,
            styleFr = style_fr,
            stylePt = style_pt,
            styleRu = style_ru,
            styleZh = style_zh,
            styleJa = style_ja,
            styleAr = style_ar,
            styleHi = style_hi,
            // Colors and location
            primaryColor = prim_color?.toInt(),
            secondaryColor = sec_color?.toInt(),
            backgroundColor = background_color?.toInt(),
            detailColor = detail_color?.toInt(),
            longitude = locationPair?.first,
            latitude = locationPair?.second,
            // LocalizedFieldSet for core DisplayableItem interface
            localizedFields = LocalizedFieldSet(
                names = buildMap {
                    put("en", paintingname ?: "")
                    paintingname_ro?.let { put("ro", it) }
                    paintingname_it?.let { put("it", it) }
                    paintingname_es?.let { put("es", it) }
                    paintingname_de?.let { put("de", it) }
                    paintingname_fr?.let { put("fr", it) }
                    paintingname_pt?.let { put("pt", it) }
                    paintingname_ru?.let { put("ru", it) }
                    paintingname_zh?.let { put("zh", it) }
                    paintingname_ja?.let { put("ja", it) }
                    paintingname_ar?.let { put("ar", it) }
                    paintingname_hi?.let { put("hi", it) }
                },
                descriptions = buildMap {
                    put("en", description ?: "")
                    description_ro?.let { put("ro", it) }
                    description_it?.let { put("it", it) }
                    description_es?.let { put("es", it) }
                    description_de?.let { put("de", it) }
                    description_fr?.let { put("fr", it) }
                    description_pt?.let { put("pt", it) }
                    description_ru?.let { put("ru", it) }
                    description_zh?.let { put("zh", it) }
                    description_ja?.let { put("ja", it) }
                    description_ar?.let { put("ar", it) }
                    description_hi?.let { put("hi", it) }
                },
                categories = buildMap {
                    put("en", style ?: "")
                    style_ro?.let { put("ro", it) }
                    style_it?.let { put("it", it) }
                    style_es?.let { put("es", it) }
                    style_de?.let { put("de", it) }
                    style_fr?.let { put("fr", it) }
                    style_pt?.let { put("pt", it) }
                    style_ru?.let { put("ru", it) }
                    style_zh?.let { put("zh", it) }
                    style_ja?.let { put("ja", it) }
                    style_ar?.let { put("ar", it) }
                    style_hi?.let { put("hi", it) }
                }
            )
        )
    }

    fun List<Museum_item>.toHeritageSites(): List<HeritageSite> {
        return map { it.toHeritageSite() }
    }
}
