package com.whitelabel.core.domain.usecase

import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository

class ToggleFavoriteUseCase<T : DisplayableItem>(
    private val repository: ItemRepository<T>
) {
    suspend operator fun invoke(item: T): Result<Unit> = repository.toggleFavorite(item)
}
