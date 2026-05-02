package com.herbal.android

import androidx.compose.material3.SnackbarDuration
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.SnackbarResult
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import androidx.navigation.navigation
import com.whitelabel.platform.presentation.screens.detail.DetailScreen
import com.whitelabel.platform.presentation.screens.home.HomeScreen
import com.whitelabel.core.presentation.home.HomeViewModel
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.platform.data.models.CatalogItem
import com.whitelabel.platform.presentation.screens.language.LanguageSelectionScreen
import com.whitelabel.platform.presentation.screens.site.SiteDetailScreen
import com.whitelabel.core.presentation.detail.ItemDetailViewModel
import com.whitelabel.core.AppConfig
import com.herbal.utils.LOG
import com.whitelabel.core.presentation.language.LanguageSelectionViewModel
import kotlinx.coroutines.launch
import org.koin.compose.koinInject
import org.koin.core.parameter.parametersOf

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    // HomeViewModel is a Koin singleton — same instance everywhere
    val homeViewModel: HomeViewModel<CatalogItem> = koinInject()

    NavHost(navController = navController, startDestination = "main_graph") {
        navigation(startDestination = "home", route = "main_graph") {
            composable("home") {
                LOG("HomeViewModel: $homeViewModel")
                val appConfig: AppConfig = koinInject()
                HomeScreen(
                    viewModel = homeViewModel,
                    appConfig = appConfig,
                    onSiteClick = { plantId -> navController.navigate("site/$plantId") },
                    onNavigateToLanguage = { navController.navigate("language") },
                    snackbarHostState = snackbarHostState
                )
            }

            composable(
                route = "site/{siteId}",
                arguments = listOf(navArgument("siteId") { type = NavType.LongType })
            ) { backStackEntry ->
                val siteId = backStackEntry.arguments?.getLong("siteId") ?: return@composable
                val viewModel: ItemDetailViewModel<CatalogItem> = koinInject { parametersOf(siteId) }
                val appConfig: AppConfig = koinInject()

                SiteDetailScreen(
                    viewModel = viewModel,
                    onBackClick = { navController.popBackStack() },
                    onShowFullImage = { id -> navController.navigate("detail/$id") },
                    onShowOnMap = { id ->
                        homeViewModel.setViewMode(ViewMode.Map)
                        homeViewModel.setFocusedItem(id)
                        navController.navigate("home") {
                            popUpTo("home") { inclusive = true }
                        }
                    },
                    appConfig = appConfig
                )
            }

            composable(
                route = "detail/{siteId}",
                arguments = listOf(navArgument("siteId") { type = NavType.LongType })
            ) { backStackEntry ->
                LOG("AppNavigation - COMPOSING detail route")
                val plantId = backStackEntry.arguments?.getLong("siteId") ?: return@composable
                val viewModel: ItemDetailViewModel<CatalogItem> = koinInject { parametersOf(plantId) }

                DetailScreen(
                    viewModel = viewModel,
                    onNavigateBack = {
                        LOG("AppNavigation - detail onNavigateBack CALLED")
                        navController.popBackStack()
                    }
                )
            }

            composable("language") {
                val viewModel: LanguageSelectionViewModel = koinInject()
                LanguageSelectionScreen(
                    viewModel = viewModel,
                    onNavigateBack = { navController.popBackStack() },
                    onLanguageChanged = { languageViewModel ->
                        navController.popBackStack()
                        scope.launch {
                            val result = snackbarHostState.showSnackbar(
                                message = "Language changed",
                                actionLabel = "UNDO",
                                duration = SnackbarDuration.Short
                            )
                            if (result == SnackbarResult.ActionPerformed) {
                                languageViewModel.undoLanguageChange()
                            }
                        }
                    }
                )
            }
        }
    }
}
