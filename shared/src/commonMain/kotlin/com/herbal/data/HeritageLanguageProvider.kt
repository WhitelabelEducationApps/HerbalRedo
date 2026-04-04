package com.herbal.data

import com.herbal.utils.LanguagePreferences
import com.herbal.utils.SupportedLanguage
import com.whitelabel.core.domain.language.LanguageProvider
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.flow.MutableStateFlow

/**
 * Adapts the existing LanguagePreferences singleton to the core LanguageProvider interface.
 */
class HeritageLanguageProvider : LanguageProvider {
    override fun getCurrentLanguageCode(): String = LanguagePreferences.getEffectiveLanguage()

    override val selectedLanguage: StateFlow<String?>
        get() {
            // Map SupportedLanguage? -> String? by wrapping the existing StateFlow
            // This is a simplification; in production you'd use a proper coroutine scope
            return object : StateFlow<String?> {
                override val value: String? get() = LanguagePreferences.selectedLanguage.value?.code
                override val replayCache: List<String?> get() = listOf(value)
                override suspend fun collect(collector: kotlinx.coroutines.flow.FlowCollector<String?>): Nothing {
                    LanguagePreferences.selectedLanguage.collect { lang ->
                        collector.emit(lang?.code)
                    }
                }
            }
        }

    override fun setLanguage(code: String?) {
        LanguagePreferences.setLanguage(code?.let { SupportedLanguage.fromCode(it) })
    }
}
