package com.herbal.utils

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object LocationFilterPreferences {
    private val _useLocationFilter = MutableStateFlow(false)
    val useLocationFilter: StateFlow<Boolean> = _useLocationFilter.asStateFlow()

    // All geographic zones the user's location falls in (e.g. ["zone_eastern_europe", "zone_southern_europe"])
    private val _currentUserZones = MutableStateFlow<List<String>>(emptyList())
    val currentUserZones: StateFlow<List<String>> = _currentUserZones.asStateFlow()

    private var persistence: ILocationFilterPersistence? = null

    fun initPersistence(p: ILocationFilterPersistence) {
        persistence = p
        _useLocationFilter.value = p.getUseLocationFilter()
    }

    fun setUseLocationFilter(value: Boolean) {
        _useLocationFilter.value = value
        persistence?.saveUseLocationFilter(value)
    }

    fun setCurrentUserZones(zones: List<String>) {
        _currentUserZones.value = zones
    }
}

interface ILocationFilterPersistence {
    fun getUseLocationFilter(): Boolean
    fun saveUseLocationFilter(value: Boolean)
}
