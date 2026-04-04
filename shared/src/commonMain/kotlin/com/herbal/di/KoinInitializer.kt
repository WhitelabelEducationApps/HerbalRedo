package com.herbal.di

import com.whitelabel.platform.di.platformModule as whitelabelPlatformModule
import org.koin.core.context.startKoin
import org.koin.dsl.KoinAppDeclaration

fun initKoin(appDeclaration: KoinAppDeclaration = {}) = startKoin {
    appDeclaration()
    modules(
        commonModule,
        viewModelModule,
        whitelabelPlatformModule,
        appPlatformModule
    )
}
