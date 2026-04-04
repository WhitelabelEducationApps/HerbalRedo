package com.whitelabel.core.presentation.language

import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.language.SupportedLanguage
import com.whitelabel.core.presentation.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.map

/**
 * ViewModel for language selection screen.
 * Uses LanguageProvider to get/set the current language.
 */
open class LanguageSelectionViewModel(
    private val languageProvider: LanguageProvider
) : ViewModel() {

    val selectedLanguage: StateFlow<String?> = languageProvider.selectedLanguage

    private val _previousLanguageCode = MutableStateFlow<String?>(null)

    private val _languageChanged = MutableStateFlow(false)
    val languageChanged: StateFlow<Boolean> = _languageChanged.asStateFlow()

    fun setLanguage(language: SupportedLanguage?) {
        _previousLanguageCode.value = selectedLanguage.value
        languageProvider.setLanguage(language?.code)
        _languageChanged.value = true
    }

    fun undoLanguageChange() {
        val previousCode = _previousLanguageCode.value
        _previousLanguageCode.value = selectedLanguage.value
        languageProvider.setLanguage(previousCode)
    }

    fun resetLanguageChangedFlag() {
        _languageChanged.value = false
    }

    fun getSupportedLanguages(): List<SupportedLanguage> {
        return SupportedLanguage.entries
    }
}
