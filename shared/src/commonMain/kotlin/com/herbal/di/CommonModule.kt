package com.herbal.di

import coil3.ImageLoader
import coil3.PlatformContext
import coil3.annotation.ExperimentalCoilApi
import com.whitelabel.platform.data.CatalogLanguageProvider
import com.whitelabel.platform.data.datasource.CatalogLocalDataSource
import com.whitelabel.platform.data.repository.CatalogRepository
import com.herbal.utils.ImagePreloader
import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.domain.usecase.GetItemDetailUseCase
import com.whitelabel.core.domain.usecase.GetItemsUseCase
import com.whitelabel.core.domain.usecase.SearchItemsUseCase
import com.whitelabel.core.domain.usecase.ToggleFavoriteUseCase
import com.whitelabel.core.presentation.home.ItemGrouper
import com.whitelabel.platform.data.models.CatalogItem
import com.whitelabel.platform.presentation.HeritageItemGrouper
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
        com.herbal.utils.LOG("DI - Creating CatalogLocalDataSource (SINGLETON)")
        CatalogLocalDataSource(get(), get())
    }

    // Repository - bind to interface to enable testing and decoupling
    single<ItemRepository<CatalogItem>> {
        com.herbal.utils.LOG("DI - Creating CatalogRepository (SINGLETON)")
        CatalogRepository(get()) { com.whitelabel.platform.utils.LocalizationManager.getCurrentLanguageCode() }
    }

    // Language Provider - Singleton
    single<LanguageProvider> { CatalogLanguageProvider() }

    // Use Cases - Factory
    factory {
        com.herbal.utils.LOG("DI - Creating NEW GetItemsUseCase")
        GetItemsUseCase(get<ItemRepository<CatalogItem>>())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW SearchItemsUseCase")
        SearchItemsUseCase(get<ItemRepository<CatalogItem>>(), get())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW ToggleFavoriteUseCase")
        ToggleFavoriteUseCase(get<ItemRepository<CatalogItem>>())
    }
    factory {
        com.herbal.utils.LOG("DI - Creating NEW GetItemDetailUseCase")
        GetItemDetailUseCase(get<ItemRepository<CatalogItem>>())
    }

    // ItemGrouper - Heritage-specific: groups by country
    single<ItemGrouper<CatalogItem>> { HeritageItemGrouper() }

    // Image Preloader - Singleton
    single { (context: PlatformContext) ->
        com.herbal.utils.LOG("DI - Creating ImagePreloader (SINGLETON)")
        ImagePreloader(context, ImageLoader(context))
    }
}
