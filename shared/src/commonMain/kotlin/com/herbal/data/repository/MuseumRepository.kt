package com.herbal.data.repository

import com.herbal.data.datasource.HeritageSiteLocalDataSource
import com.herbal.data.mapper.HeritageSiteMapper.toHeritageSite
import com.herbal.data.mapper.HeritageSiteMapper.toHeritageSites
import com.herbal.data.models.Country
import com.herbal.data.models.HeritageSite
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.model.GroupMetadata
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onEach

/**
 * Concrete implementation backed by HeritageSiteLocalDataSource.
 * Implements IMuseumRepository so higher layers depend on the interface.
 */
class MuseumRepository(private val dataSource: HeritageSiteLocalDataSource) : IMuseumRepository {

    override fun getAllSites(): Flow<Result<List<HeritageSite>>> {
        com.herbal.utils.LOG("MuseumRepository.getAllSites() - CALLED")
        return dataSource.getAllSites()
            .map<List<com.herbal.data.local.Museum_item>, Result<List<HeritageSite>>> {
                com.herbal.utils.LOG("MuseumRepository.getAllSites() - Mapping ${it.size} items")
                com.herbal.utils.checkMainThread()
                val result = com.herbal.utils.measureTimeAndLog("getAllSites mapping ${it.size} items") {
                    it.toHeritageSites()
                }
                Result.Success(result)
            }
            .catch {
                com.herbal.utils.LOG("MuseumRepository.getAllSites() - ERROR: ${it.message}")
                emit(Result.Error(it))
            }
    }

    override fun getSiteById(id: Long): Flow<Result<HeritageSite?>> {
        com.herbal.utils.LOG("MuseumRepository.getSiteById() - CALLED for id=$id")
        return dataSource.getSiteById(id).onEach {
            items ->
                com.herbal.utils.LOG("MuseumRepository.getSiteById() - DataSource EMITTED ${items?.size ?: 0} items")
                com.herbal.utils.checkMainThread()
            }
            .map<List<com.herbal.data.local.Museum_item>?, Result<HeritageSite?>> { it ->
                val result = com.herbal.utils.measureTimeAndLog("getSiteById($id) mapping") {
                    val firstItem = it?.firstOrNull()
                    if (firstItem == null) {
                        com.herbal.utils.LOG("MuseumRepository.getSiteById() - Site NOT FOUND for id=$id")
                        Result.Error(Exception("Site not found"))
                    }
                    else {
                        com.herbal.utils.LOG("MuseumRepository.getSiteById() - Site FOUND: ${firstItem.paintingname}")
                        Result.Success(firstItem.toHeritageSite())
                    }
                }
                result
            }
            .catch {
                com.herbal.utils.LOG("MuseumRepository.getSiteById() - ERROR: ${it.message}")
                emit(Result.Error(it))
            }
    }

    override fun getFavoriteSites(): Flow<Result<List<HeritageSite>>> =
        dataSource.getFavoriteSites()
            .map<List<com.herbal.data.local.Museum_item>, Result<List<HeritageSite>>> {
                Result.Success(it.toHeritageSites())
            }
            .catch { emit(Result.Error(it)) }

    override fun searchSites(query: String): Flow<Result<List<HeritageSite>>> =
        dataSource.searchSites(query)
            .map<List<com.herbal.data.local.Museum_item>, Result<List<HeritageSite>>> {
                Result.Success(it.toHeritageSites())
            }
            .catch { emit(Result.Error(it)) }

    override suspend fun markAsViewed(itemId: Long): Result<Unit> {
        com.herbal.utils.LOG("MuseumRepository.markAsViewed() - CALLED for site $itemId")
        return try {
            dataSource.markAsViewed(itemId)
            com.herbal.utils.LOG("MuseumRepository.markAsViewed() - SUCCESS")
            Result.Success(Unit)
        } catch (e: Exception) {
            com.herbal.utils.LOG("MuseumRepository.markAsViewed() - ERROR: ${e.message}")
            Result.Error(e)
        }
    }

    override suspend fun getSiteCount(): Result<Long> {
        return try {
            Result.Success(dataSource.getCount())
        } catch (e: Exception) {
            Result.Error(e)
        }
    }

    override suspend fun getCountryTranslations(countryNames: List<String>): Result<Map<String, Country>> {
        return Result.Success(emptyMap())
    }

    // === ItemRepository<HeritageSite> core interface methods ===

    override fun getAllItems(): Flow<Result<List<HeritageSite>>> = getAllSites()

    override fun getItemById(id: Long): Flow<Result<HeritageSite?>> = getSiteById(id)

    override fun getFavoriteItems(): Flow<Result<List<HeritageSite>>> = getFavoriteSites()

    override fun searchItems(query: String, languageCode: String): Flow<Result<List<HeritageSite>>> =
        searchSites(query) // TODO: pass languageCode to datasource in Phase 4

    override suspend fun toggleFavorite(item: HeritageSite): Result<Unit> {
        com.herbal.utils.LOG("MuseumRepository.toggleFavorite() - CALLED for site ${item.id}, newValue=${!item.isFavorite}")
        return try {
            dataSource.updateFavorite(item.id, !item.isFavorite)
            com.herbal.utils.LOG("MuseumRepository.toggleFavorite() - SUCCESS")
            Result.Success(Unit)
        } catch (e: Exception) {
            com.herbal.utils.LOG("MuseumRepository.toggleFavorite() - ERROR: ${e.message}")
            Result.Error(e)
        }
    }

    override suspend fun getItemCount(): Result<Long> = getSiteCount()

    override suspend fun getGroupMetadata(groupKeys: List<String>): Result<Map<String, GroupMetadata>> {
        return when (val result = getCountryTranslations(groupKeys)) {
            is Result.Success -> Result.Success(result.data.mapValues { it.value as GroupMetadata })
            is Result.Error -> Result.Error(result.exception)
        }
    }
}