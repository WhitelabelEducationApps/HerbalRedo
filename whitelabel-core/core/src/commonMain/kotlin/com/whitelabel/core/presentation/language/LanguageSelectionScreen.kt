package com.whitelabel.core.presentation.language

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

/**
 * Reusable language selection screen.
 * Works with core LanguageSelectionViewModel and SupportedLanguage.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageSelectionScreen(
    viewModel: LanguageSelectionViewModel,
    onNavigateBack: () -> Unit,
    onLanguageChanged: (LanguageSelectionViewModel) -> Unit = {},
    title: String = "Language / Limba / Langue",
    automaticLabel: String = "Automatic (Default)",
    modifier: Modifier = Modifier
) {
    val selectedLanguage by viewModel.selectedLanguage.collectAsState()
    val languageChanged by viewModel.languageChanged.collectAsState()

    LaunchedEffect(languageChanged) {
        if (languageChanged) {
            viewModel.resetLanguageChangedFlag()
            onLanguageChanged(viewModel)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(title) },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
        ) {
            LanguageItem(
                languageName = automaticLabel,
                languageCode = null,
                isSelected = selectedLanguage == null,
                onClick = { viewModel.setLanguage(null) }
            )
            HorizontalDivider()

            viewModel.getSupportedLanguages().forEach { language ->
                LanguageItem(
                    languageName = language.nativeName,
                    languageCode = language.code,
                    isSelected = selectedLanguage == language.code,
                    onClick = { viewModel.setLanguage(language) }
                )
                HorizontalDivider()
            }
        }
    }
}

@Composable
private fun LanguageItem(
    languageName: String,
    languageCode: String?,
    isSelected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 12.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column {
            Text(
                text = languageName,
                style = MaterialTheme.typography.bodyLarge
            )
            if (languageCode != null) {
                Text(
                    text = languageCode.uppercase(),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        if (isSelected) {
            Icon(
                imageVector = Icons.Filled.Check,
                contentDescription = "Selected",
                tint = MaterialTheme.colorScheme.primary
            )
        }
    }
}
