package com.whitelabel.core.presentation.home

import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.ItemGroup
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.domain.usecase.GetItemsUseCase
import com.whitelabel.core.domain.usecase.SearchItemsUseCase
import com.whitelabel.core.domain.usecase.ToggleFavoriteUseCase
import com.whitelabel.core.presentation.ViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * Generic home screen ViewModel. Works with any DisplayableItem type.
 * Grouping logic is delegated to [ItemGrouper] (strategy pattern).
 */
open class HomeViewModel<T : DisplayableItem>(
    private val getItemsUseCase: GetItemsUseCase<T>,
    private val searchItemsUseCase: SearchItemsUseCase<T>,
    private val toggleFavoriteUseCase: ToggleFavoriteUseCase<T>,
    private val repository: ItemRepository<T>,
    private val itemGrouper: ItemGrouper<T>,
    private val languageProvider: LanguageProvider,
    private val coroutineScope: CoroutineScope
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _uiState = MutableStateFlow<HomeUiState>(HomeUiState.Loading)
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    private val _viewMode = MutableStateFlow(ViewMode.Grid)
    val viewMode: StateFlow<ViewMode> = _viewMode.asStateFlow()

    private val _focusedItemId = MutableStateFlow<Long?>(null)
    val focusedItemId: StateFlow<Long?> = _focusedItemId.asStateFlow()

    private val refreshTrigger = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    init {
        loadItems()
    }

    @OptIn(ExperimentalCoroutinesApi::class)
    private fun loadItems() {
        coroutineScope.launch {
            combine(
                searchQuery,
                languageProvider.selectedLanguage,
                refreshTrigger.onStart { emit(Unit) }
            ) { query, _, _ -> query }
                .flatMapLatest { query ->
                    if (query.isBlank()) getItemsUseCase() else searchItemsUseCase(query)
                }
                .collect { result ->
                    when (result) {
                        is Result.Success -> {
                            val firstFav = result.data.firstOrNull { it.isFavorite }
                            val firstItem = result.data.firstOrNull()
                            println("[HomeViewModel] Refreshed ${result.data.size} items, firstFav=$firstFav, firstItem.id=${firstItem?.id}, firstItem.isFav=${firstItem?.isFavorite}")
                        }
                        else -> {}
                    }
                    _uiState.value = when (result) {
                        is Result.Success -> {
                            if (result.data.isEmpty()) {
                                HomeUiState.Empty
                            } else {
                                val groups = itemGrouper.group(
                                    items = result.data,
                                    repository = repository,
                                    languageCode = languageProvider.getCurrentLanguageCode()
                                )
                                HomeUiState.Success(
                                    items = result.data,
                                    groups = groups
                                )
                            }
                        }
                        is Result.Error -> HomeUiState.Error(
                            result.exception.message ?: "Unknown error"
                        )
                    }
                }
        }
    }

    fun onSearchQueryChange(query: String) {
        _searchQuery.value = query
    }

    fun onFavoriteClick(item: T) {
        coroutineScope.launch {
            toggleFavoriteUseCase(item)
            delay(100) // Give DB transaction time to complete
            refreshTrigger.tryEmit(Unit)
        }
    }

    fun setViewMode(mode: ViewMode) {
        _viewMode.value = mode
    }

    fun setFocusedItem(itemId: Long?) {
        _focusedItemId.value = itemId
    }

    fun clearFocusedItem() {
        _focusedItemId.value = null
    }
}

sealed interface HomeUiState {
    data object Loading : HomeUiState
    data object Empty : HomeUiState
    data class Success<T : DisplayableItem>(
        val items: List<T>,
        val groups: List<ItemGroup<T>>
    ) : HomeUiState
    data class Error(val message: String) : HomeUiState
}

enum class ViewMode {
    Grid, Map
}
