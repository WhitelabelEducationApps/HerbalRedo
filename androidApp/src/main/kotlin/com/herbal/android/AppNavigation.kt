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
import com.herbal.presentation.screens.detail.DetailScreen
import com.herbal.presentation.screens.detail.DetailViewModel
import com.herbal.presentation.screens.home.HomeScreen
import com.herbal.presentation.screens.home.HomeViewModel
import com.whitelabel.core.AppConfig
import com.whitelabel.core.presentation.home.ViewMode
import com.herbal.presentation.screens.language.LanguageSelectionScreen
import com.herbal.presentation.screens.language.LanguageSelectionViewModel
import com.herbal.presentation.screens.site.SiteDetailScreen
import com.herbal.presentation.screens.site.SiteDetailViewModel
import com.herbal.utils.LOG
import kotlinx.coroutines.launch
import org.koin.compose.koinInject
import org.koin.core.parameter.parametersOf

@Composable
fun AppNavigation() {
    val navController = rememberNavController()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    // HomeViewModel is a Koin singleton — same instance everywhere
    val homeViewModel: HomeViewModel = koinInject()

    NavHost(navController = navController, startDestination = "main_graph") {
        navigation(startDestination = "home", route = "main_graph") {
            composable("home") {
                LOG("HomeViewModel: $homeViewModel")
                HomeScreen(
                    viewModel = homeViewModel,
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
                val viewModel: SiteDetailViewModel = koinInject { parametersOf(siteId) }
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
                LOG("AppNavigation - detail route plantId=$plantId")
                val viewModel: DetailViewModel = koinInject { parametersOf(plantId) }
                LOG("AppNavigation - DetailViewModel obtained: $viewModel")

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
