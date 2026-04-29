package com.herbal.utils

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object LocationFilterPreferences {
    private val _useLocationFilter = MutableStateFlow(false)
    val useLocationFilter: StateFlow<Boolean> = _useLocationFilter.asStateFlow()

    // The user's current geographic zone ID (e.g. "zone_central_europe"), null when unknown
    private val _currentUserZone = MutableStateFlow<String?>(null)
    val currentUserZone: StateFlow<String?> = _currentUserZone.asStateFlow()

    private var persistence: ILocationFilterPersistence? = null

    fun initPersistence(p: ILocationFilterPersistence) {
        persistence = p
        _useLocationFilter.value = p.getUseLocationFilter()
    }

    fun setUseLocationFilter(value: Boolean) {
        _useLocationFilter.value = value
        persistence?.saveUseLocationFilter(value)
    }

    fun setCurrentUserZone(zone: String?) {
        _currentUserZone.value = zone
    }
}

interface ILocationFilterPersistence {
    fun getUseLocationFilter(): Boolean
    fun saveUseLocationFilter(value: Boolean)
}
