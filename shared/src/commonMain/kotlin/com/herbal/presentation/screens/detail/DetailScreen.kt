package com.herbal.presentation.screens.detail

import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.whitelabel.core.presentation.detail.ZoomableImageScreen
import herbalredo.shared.generated.resources.Res
import herbalredo.shared.generated.resources.wallpaper
import org.jetbrains.compose.resources.ExperimentalResourceApi
import org.jetbrains.compose.resources.painterResource

@OptIn(ExperimentalResourceApi::class)
@Composable
fun DetailScreen(
    viewModel: DetailViewModel,
    onNavigateBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    ZoomableImageScreen(
        viewModel = viewModel,
        onNavigateBack = onNavigateBack,
        title = { it.getLocalizedName() },
        imageUrl = { it.imageUrl?.split(",")?.firstOrNull()?.trim() },
        wallpaperIcon = {
            Icon(
                painter = painterResource(Res.drawable.wallpaper),
                contentDescription = "Set as Wallpaper"
            )
        },
        modifier = modifier
    )
}
