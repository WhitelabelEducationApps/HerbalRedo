package com.whitelabel.core.domain.repository

import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.GroupMetadata
import com.whitelabel.core.domain.model.Result
import kotlinx.coroutines.flow.Flow

/**
 * Generic repository contract for item catalog apps.
 * Each app provides its own implementation backed by its specific DB schema.
 */
interface ItemRepository<T : DisplayableItem> {
    fun getAllItems(): Flow<Result<List<T>>>
    fun getItemById(id: Long): Flow<Result<T?>>
    fun getFavoriteItems(): Flow<Result<List<T>>>
    fun searchItems(query: String, languageCode: String): Flow<Result<List<T>>>
    suspend fun toggleFavorite(item: T): Result<Unit>
    suspend fun markAsViewed(itemId: Long): Result<Unit>
    suspend fun getItemCount(): Result<Long>
    suspend fun getGroupMetadata(groupKeys: List<String>): Result<Map<String, GroupMetadata>>
}
