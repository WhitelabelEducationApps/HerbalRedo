package com.herbal.presentation.screens.detail

import androidx.compose.material3.Icon
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import com.herbal.utils.LanguagePreferences
import com.herbal.utils.getStringResource
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
    val selectedLanguage by LanguagePreferences.selectedLanguage.collectAsState()
    val languageCode = selectedLanguage?.code ?: "en"

    ZoomableImageScreen(
        viewModel = viewModel,
        onNavigateBack = onNavigateBack,
        title = { it.getLocalizedName(languageCode) },
        imageUrl = { it.imageUrl?.split(",")?.firstOrNull()?.trim() },
        wallpaperIcon = {
            Icon(
                painter = painterResource(Res.drawable.wallpaper),
                contentDescription = getStringResource("set_wallpaper")
            )
        },
        backDescription = getStringResource("back"),
        wallpaperSuccessMessage = getStringResource("wallpaper_success"),
        modifier = modifier
    )
}
