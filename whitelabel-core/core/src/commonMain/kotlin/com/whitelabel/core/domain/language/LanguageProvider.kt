package com.whitelabel.core.domain.language

import kotlinx.coroutines.flow.StateFlow

/**
 * Provides current language state. Apps implement this
 * wrapping their own language/locale management.
 */
interface LanguageProvider {
    fun getCurrentLanguageCode(): String
    val selectedLanguage: StateFlow<String?>
    fun setLanguage(code: String?)
}
