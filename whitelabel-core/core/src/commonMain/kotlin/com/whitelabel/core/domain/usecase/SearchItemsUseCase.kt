package com.whitelabel.core.domain.usecase

import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import kotlinx.coroutines.flow.Flow

class SearchItemsUseCase<T : DisplayableItem>(
    private val repository: ItemRepository<T>,
    private val languageProvider: LanguageProvider
) {
    operator fun invoke(query: String): Flow<Result<List<T>>> {
        return if (query.isBlank()) {
            repository.getAllItems()
        } else {
            repository.searchItems(query, languageProvider.getCurrentLanguageCode())
        }
    }
}
