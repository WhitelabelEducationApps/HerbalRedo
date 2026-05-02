package com.herbal.di

import com.whitelabel.platform.data.local.DatabaseDriverFactory
import com.whitelabel.core.AppConfig
import org.koin.android.ext.koin.androidContext
import org.koin.dsl.module

actual val appPlatformModule = module {
    single { DatabaseDriverFactory(androidContext(), "plants.db") }
    single { AppConfig(enableMap = false, enableCategories = false, enableLocationFilter = true) }
}
