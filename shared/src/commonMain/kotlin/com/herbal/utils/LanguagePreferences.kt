package com.herbal.utils

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object LanguagePreferences {
    private val _selectedLanguage = MutableStateFlow<SupportedLanguage?>(null)
    val selectedLanguage: StateFlow<SupportedLanguage?> = _selectedLanguage.asStateFlow()

    fun setLanguage(language: SupportedLanguage?) {
        _selectedLanguage.value = language
    }

    fun getEffectiveLanguage(): String {
        return _selectedLanguage.value?.code ?: LocalizationManager.getCurrentLanguageCode()
    }
}
