package com.whitelabel.core.presentation.detail

import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil3.compose.AsyncImage
import coil3.compose.LocalPlatformContext
import coil3.request.ImageRequest
import com.whitelabel.core.domain.model.DisplayableItem
import com.whitelabel.core.presentation.components.LoadingIndicator

/**
 * Full-screen zoomable image viewer with wallpaper support.
 * Generic — works with any DisplayableItem.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun <T : DisplayableItem> ZoomableImageScreen(
    viewModel: ItemDetailViewModel<T>,
    onNavigateBack: () -> Unit,
    title: (T) -> String,
    imageUrl: (T) -> String? = { it.imageUrls.firstOrNull() },
    wallpaperIcon: @Composable () -> Unit = {},
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val wallpaperStatus by viewModel.wallpaperStatus.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(wallpaperStatus) {
        when (wallpaperStatus) {
            is WallpaperStatus.Success -> {
                snackbarHostState.showSnackbar("Wallpaper set successfully!")
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
    val item = (uiState as? ItemDetailUiState.Success<T>)?.item

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(item?.let(title) ?: "Detail") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        },
        floatingActionButton = {
            if (uiState is ItemDetailUiState.Success<*>) {
                FloatingActionButton(
                    onClick = { viewModel.setAsWallpaper() },
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ) {
                    if (wallpaperStatus is WallpaperStatus.Loading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    } else {
                        wallpaperIcon()
                    }
                }
            }
        },
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Box(modifier = modifier.fillMaxSize().padding(paddingValues)) {
            when (uiState) {
                is ItemDetailUiState.Loading -> LoadingIndicator()
                is ItemDetailUiState.Error -> {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        Text((uiState as ItemDetailUiState.Error).message)
                    }
                }
                is ItemDetailUiState.Success<*> -> {
                    val url = item?.let(imageUrl)
                    ZoomableImage(
                        imageUrl = url,
                        contentDescription = item?.let(title) ?: ""
                    )
                }
            }
        }
    }
}

@Composable
fun ZoomableImage(
    imageUrl: String?,
    contentDescription: String,
    modifier: Modifier = Modifier
) {
    var scale by remember { mutableStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    val context = LocalPlatformContext.current

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, _ ->
                    scale = (scale * zoom).coerceIn(1f, 5f)
                    if (scale > 1f) {
                        offset = Offset(
                            x = (offset.x + pan.x).coerceIn(-size.width.toFloat(), size.width.toFloat()),
                            y = (offset.y + pan.y).coerceIn(-size.height.toFloat(), size.height.toFloat())
                        )
                    } else {
                        offset = Offset.Zero
                    }
                }
            },
        contentAlignment = Alignment.Center
    ) {
        if (imageUrl.isNullOrBlank()) {
            Text("No image available")
        } else {
            AsyncImage(
                model = ImageRequest.Builder(context)
                    .data(imageUrl)
                    .build(),
                contentDescription = contentDescription,
                modifier = Modifier
                    .fillMaxSize()
                    .graphicsLayer(
                        scaleX = scale,
                        scaleY = scale,
                        translationX = offset.x,
                        translationY = offset.y
                    ),
                contentScale = ContentScale.Fit
            )
        }
    }
}
