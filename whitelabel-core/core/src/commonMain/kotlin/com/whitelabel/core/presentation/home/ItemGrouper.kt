package com.whitelabel.core.presentation.home

import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.ItemGroup
import com.whitelabel.core.domain.repository.ItemRepository

/**
 * Strategy interface for grouping items.
 * Heritage app groups by country, art app might group by artist or era.
 */
interface ItemGrouper<T : DisplayableItem> {
    suspend fun group(
        items: List<T>,
        repository: ItemRepository<T>,
        languageCode: String
    ): List<ItemGroup<T>>
}
