package com.herbal.di


import com.whitelabel.core.domain.language.LanguageProvider
import com.whitelabel.core.domain.repository.ItemRepository
import com.whitelabel.core.domain.usecase.GetItemDetailUseCase
import com.whitelabel.core.presentation.detail.ItemDetailViewModel
import com.whitelabel.core.presentation.home.HomeViewModel
import com.whitelabel.core.presentation.home.ItemGrouper
import com.whitelabel.core.presentation.language.LanguageSelectionViewModel
import com.whitelabel.platform.data.models.CatalogItem
import com.whitelabel.platform.utils.LocationFilterPreferences
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.combine
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
        val locationFilter = combine(
            LocationFilterPreferences.useLocationFilter,
            LocationFilterPreferences.currentUserZones
        ) { use, zones ->
            if (!use || zones.isEmpty()) { _: CatalogItem -> true }
            else { item: CatalogItem ->
                item.countries.isEmpty() || item.countries.any { it in zones }
            }
        }
        HomeViewModel(
            getItemsUseCase = get(),
            searchItemsUseCase = get(),
            toggleFavoriteUseCase = get(),
            repository = get<ItemRepository<CatalogItem>>(),
            itemGrouper = get<ItemGrouper<CatalogItem>>(),
            languageProvider = get(),
            coroutineScope = get(),
            itemFilter = locationFilter
        )
    }

    // ItemDetailViewModel<HeritageSite> - Factory with parameter
    // Both SiteDetailViewModel and DetailViewModel are typealiases to this type
    factory { params ->
        val siteId = params.get<Long>()
        com.herbal.utils.LOG("DI - Creating NEW ItemDetailViewModel for siteId=$siteId")
        ItemDetailViewModel<CatalogItem>(
            itemId = siteId,
            getItemDetailUseCase = get<GetItemDetailUseCase<CatalogItem>>(),
            toggleFavoriteUseCase = get(),
            repository = get<ItemRepository<CatalogItem>>(),
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
