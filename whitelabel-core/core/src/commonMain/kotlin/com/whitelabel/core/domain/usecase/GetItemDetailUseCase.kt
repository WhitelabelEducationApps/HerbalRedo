package com.whitelabel.core.domain.usecase

import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import kotlinx.coroutines.flow.Flow

class GetItemDetailUseCase<T : DisplayableItem>(
    private val repository: ItemRepository<T>
) {
    operator fun invoke(id: Long): Flow<Result<T?>> = repository.getItemById(id)
}
