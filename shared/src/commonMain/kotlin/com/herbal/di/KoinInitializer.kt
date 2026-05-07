package com.herbal.di

import com.whitelabel.platform.di.commonModule
import com.whitelabel.platform.di.platformModule as whitelabelPlatformModule
import com.whitelabel.platform.di.viewModelModule
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
