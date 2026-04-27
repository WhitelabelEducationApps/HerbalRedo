package com.herbal.presentation.screens.home

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.rememberDrawerState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import com.herbal.utils.LOG
import com.whitelabel.core.AppConfig
import com.whitelabel.core.presentation.home.ViewMode
import com.whitelabel.platform.utils.debugLogD
import com.whitelabel.platform.utils.logFunctionEntry
import com.whitelabel.platform.utils.logLifecycle
import com.whitelabel.platform.utils.logStateChange
import com.whitelabel.platform.utils.logUserAction
import kotlinx.coroutines.launch
import org.koin.compose.koinInject

private const val TAG = "HomeScreen"

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel,
    onSiteClick: (Long) -> Unit,
    onNavigateToLanguage: () -> Unit,
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() },
    modifier: Modifier = Modifier
) {
    logLifecycle(TAG, "Composable entered")

    val uiState by viewModel.uiState.collectAsState()
    val searchQuery by viewModel.searchQuery.collectAsState()
    val viewMode by viewModel.viewMode.collectAsState()
    val focusedSiteId by viewModel.focusedItemId.collectAsState()
    val appConfig: AppConfig = koinInject()
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val scope = rememberCoroutineScope()
    var searchActive by rememberSaveable { mutableStateOf(false) }
    
    // Log state changes
    DisposableEffect(uiState) {
        debugLogD(TAG, "uiState updated: ${uiState.javaClass.simpleName}")
        onDispose { }
    }
    
    DisposableEffect(viewMode) {
        logStateChange(TAG, "viewMode", null, viewMode)
        onDispose { }
    }
    
    DisposableEffect(searchQuery) {
        if (searchQuery.isNotEmpty()) {
            debugLogD(TAG, "searchQuery: '$searchQuery'")
        }
        onDispose { }
    }
    
    DisposableEffect(focusedSiteId) {
        if (focusedSiteId != null) {
            debugLogD(TAG, "focusedSiteId: $focusedSiteId")
        }
        onDispose { }
    }

    ModalNavigationDrawer(
        drawerState = drawerState,
        gesturesEnabled = viewMode != ViewMode.Map,
        drawerContent = {
            logLifecycle(TAG, "Drawer content composed")
            HomeDrawerContent(
                viewMode = viewMode,
                onViewModeChange = { newMode ->
                    logUserAction(TAG, "switched view mode", "from $viewMode to $newMode")
                    viewModel.setViewMode(newMode)
                },
                onLanguageClick = {
                    logUserAction(TAG, "opened language selection")
                    onNavigateToLanguage()
                },
                appConfig = appConfig,
                onCloseDrawer = { scope.launch { drawerState.close() } }
            )
        }
    ) {
        Scaffold(
            topBar = {
                HomeTopAppBar(
                    searchActive = searchActive,
                    searchQuery = searchQuery,
                    onSearchQueryChange = { query ->
                        if (query != searchQuery) {
                            debugLogD(TAG, "search query changed: '$query'")
                        }
                        viewModel.onSearchQueryChange(query)
                    },
                    onSearchActiveChange = { active ->
                        logStateChange(TAG, "searchActive", searchActive, active)
                        searchActive = active
                    },
                    onOpenDrawer = {
                        logUserAction(TAG, "opened navigation drawer")
                        scope.launch { drawerState.open() }
                    }
                )
            },
            snackbarHost = {
                SnackbarHost(hostState = snackbarHostState)
            }
        ) { paddingValues ->
            Column(
                modifier = modifier.fillMaxSize().padding(paddingValues)
            ) {
                HomeContent(
                    uiState = uiState,
                    viewMode = viewMode,
                    searchQuery = searchQuery,
                    focusedSiteId = focusedSiteId,
                    onSiteClick = { siteId ->
                        logUserAction(TAG, "clicked site", "siteId=$siteId")
                        onSiteClick(siteId)
                    },
                    onFavoriteClick = { site ->
                        logUserAction(TAG, "toggled favorite", "siteId=${site.id}, name=${site.name}")
                        viewModel.onFavoriteClick(site)
                    },
                    onClearFocusedSite = {
                        debugLogD(TAG, "clearing focused site")
                        viewModel.clearFocusedItem()
                    },
                    showCategory = appConfig.enableCategories
                )
            }
        }
    }
}
