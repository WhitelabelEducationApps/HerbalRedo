package com.herbal.data.datasource

import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import com.herbal.data.local.DatabaseDriverFactory
import com.herbal.data.local.HerbalDatabase
import com.herbal.data.local.Museum_item
import com.herbal.utils.LocalizationManager
import com.herbal.utils.SupportedLanguage
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.flow.onEach
import kotlinx.coroutines.withContext

class HeritageSiteLocalDataSource(
    driverFactory: DatabaseDriverFactory,
    private val dispatcher: CoroutineDispatcher
) {
    private val database = HerbalDatabase(driverFactory.createDriver())
    private val heritageQueries = database.heritageSiteQueries
    private val authorQueries = database.authorsQueries

    fun getAllSites(): Flow<List<Museum_item>> {
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.getAllSites() - CALLED, creating Flow")
        return heritageQueries.selectAll()
            .asFlow()
            .mapToList(dispatcher)
            .onEach { list ->
                val item1 = list.find { it.id == 1L }
                val item2 = list.find { it.id == 2L }
                com.herbal.utils.LOG("HeritageSiteLocalDataSource.getAllSites() - EMITTED ${list.size} items, item1.isFav=${item1?.isFavourite}, item2.isFav=${item2?.isFavourite}")
            }
            .flowOn(dispatcher)
    }

    fun getSiteById(id: Long): Flow<List<Museum_item>?> {
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.getSiteById() - CALLED for id=$id, creating Flow")
        return heritageQueries.selectById(id)
            .asFlow()
            .mapToList(dispatcher).onEach {
                items ->
                com.herbal.utils.LOG("HeritageSiteLocalDataSource.getSiteById() - Database EMITTED ${items?.size ?: 0} items for id=$id")
            }
            .flowOn(dispatcher)
    }

    fun getFavoriteSites(): Flow<List<Museum_item>> {
        return heritageQueries.selectFavorites()
            .asFlow()
            .mapToList(dispatcher)
            .flowOn(dispatcher)
    }

    fun searchSites(query: String): Flow<List<Museum_item>> {
        val languageCode = LocalizationManager.getCurrentLanguageCode()
        val language = SupportedLanguage.fromCode(languageCode)

        val searchQuery = when (language) {
            SupportedLanguage.ROMANIAN -> heritageQueries.searchByNameRo(query)
            SupportedLanguage.ITALIAN -> heritageQueries.searchByNameIt(query)
            SupportedLanguage.SPANISH -> heritageQueries.searchByNameEs(query)
            SupportedLanguage.GERMAN -> heritageQueries.searchByNameDe(query)
            SupportedLanguage.FRENCH -> heritageQueries.searchByNameFr(query)
            SupportedLanguage.PORTUGUESE -> heritageQueries.searchByNamePt(query)
            SupportedLanguage.RUSSIAN -> heritageQueries.searchByNameRu(query)
            SupportedLanguage.CHINESE -> heritageQueries.searchByNameZh(query)
            SupportedLanguage.JAPANESE -> heritageQueries.searchByNameJa(query)
            else -> heritageQueries.searchByName(query)  // Default to English for unsupported languages
        }

        return searchQuery
            .asFlow()
            .mapToList(dispatcher)
            .flowOn(dispatcher)
    }

    suspend fun updateFavorite(id: Long, isFavorite: Boolean) {
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.updateFavorite() - CALLED id=$id, isFavorite=$isFavorite")
        withContext(dispatcher) {
            database.transaction {
                heritageQueries.updateFavorite(
                    isFavourite = if (isFavorite) "true" else "false",
                    id = id
                )
            }
        }
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.updateFavorite() - COMPLETE, DATABASE UPDATED")
    }

    suspend fun markAsViewed(id: Long) {
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.markAsViewed() - CALLED id=$id")
        withContext(dispatcher) {
            heritageQueries.updateViewed("true", id)
        }
        com.herbal.utils.LOG("HeritageSiteLocalDataSource.markAsViewed() - COMPLETE, DATABASE UPDATED")
    }

    suspend fun getCount(): Long {
        return withContext(dispatcher) {
            heritageQueries.countAll().executeAsOne()
        }
    }
}
