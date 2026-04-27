package com.herbal.utils

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object LanguagePreferences {
    private val _selectedLanguage = MutableStateFlow<SupportedLanguage?>(null)
    val selectedLanguage: StateFlow<SupportedLanguage?> = _selectedLanguage.asStateFlow()

    private var persistence: ILanguagePersistence? = null

    fun initPersistence(persistence: ILanguagePersistence) {
        this.persistence = persistence
        // Load saved language on initialization
        val savedLanguage = persistence.getSavedLanguage()
        if (savedLanguage != null) {
            _selectedLanguage.value = SupportedLanguage.fromCode(savedLanguage)
        }
    }

    fun setLanguage(language: SupportedLanguage?) {
        _selectedLanguage.value = language
        persistence?.saveLanguage(language?.code)
    }

    fun getEffectiveLanguage(): String {
        return _selectedLanguage.value?.code ?: LocalizationManager.getCurrentLanguageCode()
    }
}

interface ILanguagePersistence {
    fun getSavedLanguage(): String?
    fun saveLanguage(languageCode: String?)
}
