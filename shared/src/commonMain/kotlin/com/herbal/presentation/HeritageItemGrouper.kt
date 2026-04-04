package com.herbal.presentation

import com.herbal.data.models.HeritageSite
import com.whitelabel.core.domain.model.ItemGroup
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.presentation.home.ItemGrouper

/**
 * Heritage-specific grouper: groups sites by country.
 * A single site can belong to multiple countries (comma-separated author field).
 */
class HeritageItemGrouper : ItemGrouper<HeritageSite> {

    override suspend fun group(
        items: List<HeritageSite>,
        repository: ItemRepository<HeritageSite>,
        languageCode: String
    ): List<ItemGroup<HeritageSite>> {
        // Flatten: a site with multiple countries appears in each group
        val flattenedPairs: List<Pair<String, HeritageSite>> = items.flatMap { site ->
            site.countries.map { country -> country to site }
        }

        val grouped: Map<String, List<Pair<String, HeritageSite>>> =
            flattenedPairs.groupBy { it.first }

        // Fetch group metadata (country translations)
        val countryKeys = grouped.keys.toList()
        val metadataMap = when (val result = repository.getGroupMetadata(countryKeys)) {
            is Result.Success -> result.data
            is Result.Error -> emptyMap()
        }

        return grouped.entries
            .sortedBy { it.key }
            .map { (countryName, pairs) ->
                val displayName = metadataMap[countryName]
                    ?.getLocalizedName(languageCode)
                    ?: countryName

                ItemGroup(
                    key = countryName,
                    displayName = displayName,
                    items = pairs.map { it.second }.sortedBy { it.name }
                )
            }
    }
}
