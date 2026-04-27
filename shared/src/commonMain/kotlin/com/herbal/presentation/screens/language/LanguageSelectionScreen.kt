package com.herbal.presentation.screens.language

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.herbal.utils.getStringResource
import com.whitelabel.core.presentation.language.LanguageSelectionScreen as CoreLanguageSelectionScreen
import com.whitelabel.core.presentation.language.LanguageSelectionViewModel as CoreLanguageSelectionViewModel

@Composable
fun LanguageSelectionScreen(
    viewModel: LanguageSelectionViewModel,
    onNavigateBack: () -> Unit,
    onLanguageChanged: (LanguageSelectionViewModel) -> Unit = {},
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current

    CoreLanguageSelectionScreen(
        viewModel = viewModel,
        onNavigateBack = onNavigateBack,
        onLanguageChanged = { vm ->
            onLanguageChanged(vm)
            // Restart the activity to apply the new locale to all resources
            val activity = context as? android.app.Activity
            activity?.recreate()
        },
        title = getStringResource("select_language"),
        automaticLabel = getStringResource("automatic"),
        backDescription = getStringResource("back"),
        selectedDescription = getStringResource("selected"),
        modifier = modifier
    )
}
