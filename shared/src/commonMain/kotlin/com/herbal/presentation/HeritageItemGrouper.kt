package com.herbal.presentation

import com.herbal.data.models.HeritageSite
import com.whitelabel.core.domain.model.ItemGroup
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.presentation.home.ItemGrouper

/**
 * Groups plants by style (medicinal category). Each plant belongs to one style,
 * and style_ro/style_it/etc. translations are already in the item's localizedFields.
 */
class HeritageItemGrouper : ItemGrouper<HeritageSite> {

    override suspend fun group(
        items: List<HeritageSite>,
        repository: ItemRepository<HeritageSite>,
        languageCode: String
    ): List<ItemGroup<HeritageSite>> {
        val grouped = items.groupBy { it.style ?: "" }

        return grouped.entries
            .filter { it.key.isNotBlank() }
            .sortedBy { it.key }
            .map { (styleKey, sites) ->
                val displayName = sites.first()
                    .localizedFields.getCategory(languageCode)
                    ?: styleKey

                ItemGroup(
                    key = styleKey,
                    displayName = displayName,
                    items = sites.sortedBy { it.name }
                )
            }
    }
}
