package com.herbal.di

import coil3.ImageLoader
import coil3.PlatformContext
import coil3.annotation.ExperimentalCoilApi
import com.herbal.data.HeritageLanguageProvider
import com.herbal.data.datasource.HeritageSiteLocalDataSource
import com.herbal.data.repository.IMuseumRepository
import com.herbal.data.repository.MuseumRepository
import com.herbal.domain.usecases.GetSitesUseCase
import com.herbal.domain.usecases.SearchSiteUseCase
import com.herbal.domain.usecases.ToggleFavoriteUseCase
import com.herbal.presentation.HeritageItemGrouper
import com.herbal.utils.ImagePreloader
import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.usecase.GetItemDetailUseCase
import com.whitelabel.core.presentation.home.ItemGrouper
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import org.koin.dsl.module

@OptIn(ExperimentalCoilApi::class)
val commonModule = module {
    // Dispatcher - Singleton
    single<CoroutineDispatcher> {
        com.herbal.utils.LOG("DI - Creating CoroutineDispatcher (SINGLETON)")
        Dispatchers.Default
    }

    // Data Source - Singleton
    single {
        com.herbal.utils.LOG("DI - Creating HeritageSiteLocalDataSource (SINGLETON)")
        HeritageSiteLocalDataSource(get(), get())
    }

    // Repository - bind to interface to enable testing and decoupling
    single<IMuseumRepository> {
        com.herbal.utils.LOG("DI - Creating MuseumRepository (SINGLETON)")
        MuseumRepository(get())
    }

    // Language Provider - Singleton
    single<LanguageProvider> { HeritageLanguageProvider() }

    // Use Cases - Factory (now backed by core generic use cases via typealiases)
    factory {
        com.herbal.utils.LOG("DI - Creating NEW GetSitesUseCase")
        GetSitesUseCase(get<IMuseumRepository>())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW SearchSiteUseCase")
        SearchSiteUseCase(get<IMuseumRepository>(), get())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW ToggleFavoriteUseCase")
        ToggleFavoriteUseCase(get<IMuseumRepository>())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW GetItemDetailUseCase")
        GetItemDetailUseCase(get<IMuseumRepository>())
    }

    // ItemGrouper - Heritage-specific: groups by country
    single<ItemGrouper<com.herbal.data.models.HeritageSite>> { HeritageItemGrouper() }

    // Image Preloader - Singleton
    single { (context: PlatformContext) ->
        com.herbal.utils.LOG("DI - Creating ImagePreloader (SINGLETON)")
        ImagePreloader(context, ImageLoader(context))
    }
}