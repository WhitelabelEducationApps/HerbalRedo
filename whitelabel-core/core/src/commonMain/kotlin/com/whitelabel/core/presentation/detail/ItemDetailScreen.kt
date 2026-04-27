package com.whitelabel.core.presentation.detail

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.outlined.FavoriteBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.presentation.components.EmptyState
import com.whitelabel.core.presentation.components.LoadingIndicator
import com.whitelabel.core.presentation.components.MarqueeText

/**
 * Generic detail screen scaffold. App provides content rendering via slot.
 * Handles top bar with back/favorite, wallpaper snackbar, loading/error states.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun <T : DisplayableItem> ItemDetailScreen(
    viewModel: ItemDetailViewModel<T>,
    onBackClick: () -> Unit,
    title: (T) -> String,
    topBarColor: @Composable (T) -> Color = { MaterialTheme.colorScheme.primaryContainer },
    topBarContentColor: @Composable (T) -> Color = { MaterialTheme.colorScheme.onPrimaryContainer },
    floatingActionButton: @Composable (T) -> Unit = {},
    content: @Composable (item: T, localizedGroupName: String?) -> Unit,
    backDescription: String = "Back",
    addFavoritesDescription: String = "Add to favorites",
    removeFavoritesDescription: String = "Remove from favorites",
    wallpaperSuccessMessage: String = "Wallpaper set successfully!"
) {
    val uiState by viewModel.uiState.collectAsState()
    val wallpaperStatus by viewModel.wallpaperStatus.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(wallpaperStatus) {
        when (wallpaperStatus) {
            is WallpaperStatus.Success -> {
                snackbarHostState.showSnackbar(wallpaperSuccessMessage)
                viewModel.resetWallpaperStatus()
            }
            is WallpaperStatus.Error -> {
                snackbarHostState.showSnackbar((wallpaperStatus as WallpaperStatus.Error).message)
                viewModel.resetWallpaperStatus()
            }
            else -> {}
        }
    }

    @Suppress("UNCHECKED_CAST")
    val successState = uiState as? ItemDetailUiState.Success<T>
    val item = successState?.item

    Scaffold(
        topBar = {
            item?.let {
                TopAppBar(
                    title = {
                        MarqueeText(
                            text = title(it),
                            style = MaterialTheme.typography.titleLarge,
                            color = topBarContentColor(it)
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = onBackClick) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = backDescription)
                        }
                    },
                    actions = {
                        IconButton(onClick = { viewModel.onFavoriteClick(it) }) {
                            Icon(
                                imageVector = if (it.isFavorite) Icons.Filled.Favorite else Icons.Outlined.FavoriteBorder,
                                contentDescription = if (it.isFavorite) removeFavoritesDescription else addFavoritesDescription,
                                tint = topBarContentColor(it)
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = topBarColor(it),
                        titleContentColor = topBarContentColor(it),
                        navigationIconContentColor = topBarContentColor(it),
                        actionIconContentColor = topBarContentColor(it)
                    )
                )
            }
        },
        floatingActionButton = {
            item?.let { floatingActionButton(it) }
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (uiState) {
                is ItemDetailUiState.Loading -> LoadingIndicator()
                is ItemDetailUiState.Success<*> -> {
                    content(item!!, successState!!.localizedGroupName)
                }
                is ItemDetailUiState.Error -> EmptyState(
                    message = (uiState as ItemDetailUiState.Error).message
                )
            }
        }
    }
}
