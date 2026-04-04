package com.herbal.presentation.screens.language

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.whitelabel.core.presentation.language.LanguageSelectionScreen as CoreLanguageSelectionScreen
import com.whitelabel.core.presentation.language.LanguageSelectionViewModel as CoreLanguageSelectionViewModel

@Composable
fun LanguageSelectionScreen(
    viewModel: LanguageSelectionViewModel,
    onNavigateBack: () -> Unit,
    onLanguageChanged: (LanguageSelectionViewModel) -> Unit = {},
    modifier: Modifier = Modifier
) {
    CoreLanguageSelectionScreen(
        viewModel = viewModel,
        onNavigateBack = onNavigateBack,
        onLanguageChanged = onLanguageChanged,
        modifier = modifier
    )
}
