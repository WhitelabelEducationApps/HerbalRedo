package com.herbal.di

import com.herbal.data.models.HeritageSite
import com.herbal.data.repository.IMuseumRepository
import com.herbal.presentation.screens.home.HomeViewModel
import com.herbal.presentation.screens.language.LanguageSelectionViewModel
import com.herbal.presentation.screens.site.SiteDetailViewModel
import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.usecase.GetItemDetailUseCase
import com.whitelabel.core.presentation.home.ItemGrouper
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import org.koin.dsl.module

val viewModelModule = module {
    // Provide a CoroutineScope for ViewModels
    factory {
        com.herbal.utils.LOG("DI - Creating NEW CoroutineScope")
        CoroutineScope(SupervisorJob() + Dispatchers.Main)
    }

    // HomeViewModel - Singleton (single instance for the entire app)
    single {
        com.herbal.utils.LOG("DI - Creating HomeViewModel (SINGLETON)")
        HomeViewModel(
            getItemsUseCase = get(),
            searchItemsUseCase = get(),
            toggleFavoriteUseCase = get(),
            repository = get<IMuseumRepository>(),
            itemGrouper = get<ItemGrouper<HeritageSite>>(),
            languageProvider = get(),
            coroutineScope = get()
        )
    }

    // ItemDetailViewModel<HeritageSite> - Factory with parameter
    // Both SiteDetailViewModel and DetailViewModel are typealiases to this type
    factory { params ->
        val siteId = params.get<Long>()
        com.herbal.utils.LOG("DI - Creating NEW ItemDetailViewModel for siteId=$siteId")
        SiteDetailViewModel(
            itemId = siteId,
            getItemDetailUseCase = get<GetItemDetailUseCase<HeritageSite>>(),
            toggleFavoriteUseCase = get(),
            repository = get<IMuseumRepository>(),
            wallpaperService = get(),
            languageProvider = get(),
            coroutineScope = get()
        )
    }

    // LanguageSelectionViewModel - Factory
    factory {
        LanguageSelectionViewModel(
            languageProvider = get()
        )
    }
}
