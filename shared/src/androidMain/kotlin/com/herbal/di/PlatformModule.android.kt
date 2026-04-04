package com.herbal.di

import com.herbal.data.local.DatabaseDriverFactory
import com.whitelabel.core.AppConfig
import org.koin.android.ext.koin.androidContext
import org.koin.dsl.module

actual val appPlatformModule = module {
    // DatabaseDriverFactory - Android implementation
    single { DatabaseDriverFactory(androidContext(), "plants.db") }
    // App configuration
    single { AppConfig(enableMap = false, enableCategories = false) }
}
