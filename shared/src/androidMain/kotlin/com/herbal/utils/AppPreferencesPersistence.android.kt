package com.herbal.utils

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

private val Context.appDataStore by preferencesDataStore(name = "app_preferences")
private val USE_LOCATION_FILTER_KEY = booleanPreferencesKey("use_location_only_plants")
private val ONBOARDING_SHOWN_KEY = booleanPreferencesKey("onboarding_shown")

class DataStoreLocationFilterPersistence(private val context: Context) : ILocationFilterPersistence {

    override fun getUseLocationFilter(): Boolean = runBlocking {
        context.appDataStore.data.first()[USE_LOCATION_FILTER_KEY] ?: false
    }

    override fun saveUseLocationFilter(value: Boolean) {
        CoroutineScope(Dispatchers.IO).launch {
            context.appDataStore.edit { it[USE_LOCATION_FILTER_KEY] = value }
        }
    }
}

class DataStoreOnboardingPersistence(private val context: Context) : IOnboardingPersistence {

    override fun getOnboardingShown(): Boolean = runBlocking {
        context.appDataStore.data.first()[ONBOARDING_SHOWN_KEY] ?: false
    }

    override fun saveOnboardingShown(value: Boolean) {
        CoroutineScope(Dispatchers.IO).launch {
            context.appDataStore.edit { it[ONBOARDING_SHOWN_KEY] = value }
        }
    }
}
