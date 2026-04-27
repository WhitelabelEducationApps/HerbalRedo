package com.herbal.utils

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

private val Context.dataStore by preferencesDataStore(name = "language_preferences")
private val SELECTED_LANGUAGE_KEY = stringPreferencesKey("selected_language")

class DataStoreLanguagePersistence(private val context: Context) : ILanguagePersistence {

    override fun getSavedLanguage(): String? {
        return runBlocking {
            context.dataStore.data.first().let { preferences ->
                preferences[SELECTED_LANGUAGE_KEY]
            }
        }
    }

    override fun saveLanguage(languageCode: String?) {
        CoroutineScope(Dispatchers.IO).launch {
            context.dataStore.edit { preferences ->
                if (languageCode == null) {
                    preferences.remove(SELECTED_LANGUAGE_KEY)
                } else {
                    preferences[SELECTED_LANGUAGE_KEY] = languageCode
                }
            }
        }
    }
}
