package com.herbal.utils

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

object OnboardingPreferences {
    private val _onboardingShown = MutableStateFlow(false)
    val onboardingShown: StateFlow<Boolean> = _onboardingShown.asStateFlow()

    private var persistence: IOnboardingPersistence? = null

    fun initPersistence(p: IOnboardingPersistence) {
        persistence = p
        _onboardingShown.value = p.getOnboardingShown()
    }

    fun markShown() {
        _onboardingShown.value = true
        persistence?.saveOnboardingShown(true)
    }
}

interface IOnboardingPersistence {
    fun getOnboardingShown(): Boolean
    fun saveOnboardingShown(value: Boolean)
}
