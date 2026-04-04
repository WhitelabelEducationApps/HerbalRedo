package com.whitelabel.core.presentation.detail

import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.domain.model.Result
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.domain.service.WallpaperService
import com.whitelabel.core.domain.usecase.GetItemDetailUseCase
import com.whitelabel.core.domain.usecase.ToggleFavoriteUseCase
import com.whitelabel.core.presentation.ViewModel
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

/**
 * Generic detail screen ViewModel. Loads a single item by ID, supports
 * favorite toggling, wallpaper setting, and group metadata resolution.
 */
open class ItemDetailViewModel<T : DisplayableItem>(
    private val itemId: Long,
    private val getItemDetailUseCase: GetItemDetailUseCase<T>,
    private val toggleFavoriteUseCase: ToggleFavoriteUseCase<T>,
    private val repository: ItemRepository<T>,
    private val wallpaperService: WallpaperService,
    private val languageProvider: LanguageProvider,
    private val coroutineScope: CoroutineScope
) : ViewModel() {

    private val _uiState = MutableStateFlow<ItemDetailUiState>(ItemDetailUiState.Loading)
    val uiState: StateFlow<ItemDetailUiState> = _uiState.asStateFlow()

    private var hasMarkedViewed = false

    private val _wallpaperStatus = MutableStateFlow<WallpaperStatus>(WallpaperStatus.Idle)
    val wallpaperStatus: StateFlow<WallpaperStatus> = _wallpaperStatus.asStateFlow()

    init {
        loadItem()
    }

    private fun loadItem() {
        coroutineScope.launch {
            combine(
                getItemDetailUseCase(itemId),
                languageProvider.selectedLanguage
            ) { result, _ -> result }
                .collect { result ->
                    _uiState.value = when (result) {
                        is Result.Success -> {
                            val item = result.data
                            if (item != null) {
                                if (!hasMarkedViewed) {
                                    hasMarkedViewed = true
                                    repository.markAsViewed(itemId)
                                }
                                // Resolve group metadata for localized display
                                val groupKey = item.groupKey
                                val localizedGroupName = if (groupKey != null) {
                                    resolveGroupName(groupKey)
                                } else null
                                ItemDetailUiState.Success(
                                    item = item,
                                    localizedGroupName = localizedGroupName
                                )
                            } else {
                                ItemDetailUiState.Error("Item not found")
                            }
                        }
                        is Result.Error -> ItemDetailUiState.Error(
                            result.exception.message ?: "Unknown error"
                        )
                    }
                }
        }
    }

    private suspend fun resolveGroupName(groupKey: String): String? {
        val keys = groupKey.split(",").map { it.trim() }.filter { it.isNotBlank() }
        if (keys.isEmpty()) return null

        val metadataResult = repository.getGroupMetadata(keys)
        val metadataMap = when (metadataResult) {
            is Result.Success -> metadataResult.data
            is Result.Error -> return keys.joinToString(", ")
        }

        val langCode = languageProvider.getCurrentLanguageCode()
        return keys.joinToString(", ") { key ->
            metadataMap[key]?.getLocalizedName(langCode) ?: key
        }
    }

    fun onFavoriteClick(item: T) {
        coroutineScope.launch {
            toggleFavoriteUseCase(item)
        }
    }

    fun setAsWallpaper() {
        val currentState = _uiState.value
        if (currentState !is ItemDetailUiState.Success<*>) return

        val imageUrl = currentState.item.imageUrls.firstOrNull()
        if (imageUrl.isNullOrBlank()) {
            _wallpaperStatus.value = WallpaperStatus.Error("No image available")
            return
        }

        coroutineScope.launch {
            _wallpaperStatus.value = WallpaperStatus.Loading
            val result = wallpaperService.setWallpaper(imageUrl)
            _wallpaperStatus.value = if (result.isSuccess) {
                WallpaperStatus.Success
            } else {
                WallpaperStatus.Error(result.exceptionOrNull()?.message ?: "Failed to set wallpaper")
            }
        }
    }

    fun resetWallpaperStatus() {
        _wallpaperStatus.value = WallpaperStatus.Idle
    }
}

sealed interface ItemDetailUiState {
    data object Loading : ItemDetailUiState
    data class Success<T : DisplayableItem>(
        val item: T,
        val localizedGroupName: String? = null
    ) : ItemDetailUiState
    data class Error(val message: String) : ItemDetailUiState
}

sealed class WallpaperStatus {
    object Idle : WallpaperStatus()
    object Loading : WallpaperStatus()
    object Success : WallpaperStatus()
    data class Error(val message: String) : WallpaperStatus()
}
