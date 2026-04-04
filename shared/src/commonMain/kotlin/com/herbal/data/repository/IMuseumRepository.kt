package com.herbal.data.repository

import com.herbal.data.models.Country
import com.herbal.data.models.HeritageSite
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import kotlinx.coroutines.flow.Flow

/**
 * Repository contract for museum data.
 * Extends the generic ItemRepository from whitelabel-core.
 * Adds heritage-specific methods not covered by the core interface.
 */
interface IMuseumRepository : ItemRepository<HeritageSite> {
    // Legacy convenience aliases — delegate to core methods during migration
    fun getAllSites(): Flow<Result<List<HeritageSite>>>
    fun getSiteById(id: Long): Flow<Result<HeritageSite?>>
    fun getFavoriteSites(): Flow<Result<List<HeritageSite>>>
    fun searchSites(query: String): Flow<Result<List<HeritageSite>>>
    suspend fun getSiteCount(): Result<Long>

    // Heritage-specific (not in core interface)
    suspend fun getCountryTranslations(countryNames: List<String>): Result<Map<String, Country>>
}
